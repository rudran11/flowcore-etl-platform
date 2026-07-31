# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import time
from typing import Any, Dict, Iterator, List, Optional
import httpx

from flowcore_shared.plugins.cdk.source import SourcePlugin
from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, StateMessage
from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
from flowcore_shared.plugins.enums import PluginType
from flowcore_shared.plugins.framework.rest import (
    Authenticator, BearerAuthenticator, BasicAuthenticator, ApiKeyAuthenticator,
    CursorPaginator, OffsetPaginator, PageNumberPaginator, Paginator,
    get_retry_after, RateLimitError, retry_on_http_transient
)
from flowcore_shared.plugins.framework.schema import infer_schema

class HttpSourcePlugin(SourcePlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="source-http",
            name="Generic REST API Source",
            version="0.1.0",
            plugin_type=PluginType.CONNECTOR,
            author="FlowCore Contributors",
            description="Extracts data from REST APIs using generic HTTP methods.",
            connector_type="Source",
            flowcore_version_constraint=">=1.0.0",
            capabilities=ConnectorCapabilities(
                supports_incremental=True,
                supports_schema_discovery=True,
                supports_parallel_read=False,
                supports_batch_write=False
            )
        )
        
    def _get_authenticator(self, config: Dict[str, Any]) -> Optional[Authenticator]:
        auth_type = config.get("auth_type")
        if auth_type == "bearer":
            return BearerAuthenticator(config["api_token"])
        elif auth_type == "basic":
            return BasicAuthenticator(config["username"], config["password"])
        elif auth_type == "api_key":
            return ApiKeyAuthenticator(config["api_key"], config.get("api_key_header", "x-api-key"))
        return None

    def _get_paginator(self, config: Dict[str, Any]) -> Optional[Paginator]:
        pag_type = config.get("pagination_type")
        if pag_type == "cursor":
            return CursorPaginator(config.get("cursor_field", "cursor"), config.get("cursor_param", "cursor"))
        elif pag_type == "offset":
            return OffsetPaginator(config.get("limit", 100), config.get("offset_param", "offset"), config.get("limit_param", "limit"))
        elif pag_type == "page":
            return PageNumberPaginator(config.get("page_param", "page"))
        return None

    @retry_on_http_transient()
    def _make_request(self, client: httpx.Client, url: str, headers: Dict[str, str], params: Dict[str, Any]) -> httpx.Response:
        response = client.get(url, headers=headers, params=params)
        if response.status_code == 429:
            retry_after = get_retry_after(response)
            time.sleep(retry_after)
            raise RateLimitError(retry_after)
        response.raise_for_status()
        return response

    def check(self, config: Dict[str, Any]) -> bool:
        if not config.get("base_url"):
            raise ValueError("Missing 'base_url' in config")
            
        # Basic check request
        url = config["base_url"].rstrip('/') + config.get("check_path", "")
        auth = self._get_authenticator(config)
        headers = auth.get_auth_headers() if auth else {}
        
        with httpx.Client() as client:
            # We use a naive GET for check. In reality, APIs may require specific endpoints
            self._make_request(client, url, headers, {})
            
        return True
        
    def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        url = config["base_url"].rstrip('/') + config.get("discover_path", "")
        stream_name = config.get("stream_name", "http_stream")
        
        auth = self._get_authenticator(config)
        headers = auth.get_auth_headers() if auth else {}
        
        with httpx.Client() as client:
            response = self._make_request(client, url, headers, {})
            data = response.json()
            
            # Assume data is a list of dicts, or wrapped in a 'data' key
            records = data.get("data", data) if isinstance(data, dict) else data
            if not isinstance(records, list):
                records = [records]
                
            schema = infer_schema(records[:100])
            return [{"stream": stream_name, "json_schema": schema}]
        
    def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
        url = config["base_url"].rstrip('/') + config.get("read_path", "")
        stream_name = config.get("stream_name", "http_stream")
        replication_key = config.get("replication_key")
        
        auth = self._get_authenticator(config)
        paginator = self._get_paginator(config)
        
        cursor_value = None
        if state and stream_name in state:
            cursor_value = state[stream_name].get(replication_key)

        with httpx.Client() as client:
            page_token = None
            max_cursor = cursor_value
            
            while True:
                headers = auth.get_auth_headers() if auth else {}
                params = paginator.get_request_params(page_token) if paginator else {}
                
                # Incremental sync query param
                if replication_key and cursor_value:
                    params[config.get("incremental_param", "since")] = cursor_value
                    
                response = self._make_request(client, url, headers, params)
                data = response.json()
                
                records = data.get("data", data) if isinstance(data, dict) else data
                if not isinstance(records, list):
                    records = [records]
                    
                for record in records:
                    yield FlowCoreMessage(
                        type=MessageType.RECORD,
                        record=RecordMessage(stream=stream_name, data=record)
                    )
                    
                    if replication_key and record.get(replication_key) is not None:
                        val = record[replication_key]
                        if max_cursor is None or str(val) > str(max_cursor):
                            max_cursor = val
                            
                if paginator:
                    page_token = paginator.next_page_token(response)
                    if not page_token:
                        break
                else:
                    break
                    
            if replication_key and max_cursor is not None:
                new_state = {stream_name: {replication_key: max_cursor}}
                yield FlowCoreMessage(
                    type=MessageType.STATE,
                    state=StateMessage(state_data=new_state)
                )
