# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import httpx
from typing import Dict, Any, Optional

class FlowCoreClientError(Exception):
    pass

class FlowCoreClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def execute_pipeline(self, pipeline_id: str, version: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Submits a pipeline execution request to the server."""
        url = f"/api/v1/pipelines/{pipeline_id}/versions/{version}/execute"
        payload = {"parameters": parameters or {}}
        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise FlowCoreClientError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise FlowCoreClientError(f"Connection error: {str(e)}")

    def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """Retrieves the status of an execution run."""
        url = f"/api/v1/runs/{run_id}"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise FlowCoreClientError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise FlowCoreClientError(f"Connection error: {str(e)}")

    def ping(self) -> bool:
        """Pings the server health endpoint."""
        url = "/api/v1/health"
        try:
            response = self.client.get(url)
            return response.status_code == 200
        except httpx.RequestError:
            raise FlowCoreClientError("Could not connect to server")
