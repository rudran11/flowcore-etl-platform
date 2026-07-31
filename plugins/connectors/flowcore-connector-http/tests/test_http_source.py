import pytest
from unittest.mock import patch, MagicMock
from httpx import Response
from flowcore_shared.plugins.cdk.messages import MessageType
from flowcore_connector_http.source import HttpSourcePlugin

@pytest.fixture
def http_source():
    return HttpSourcePlugin()

@patch('httpx.Client.get')
def test_http_source_check(mock_get, http_source):
    req = MagicMock()
    mock_get.return_value = Response(200, json={"status": "ok"}, request=req)
    config = {"base_url": "https://api.example.com/v1", "auth_type": "bearer", "api_token": "secret"}
    assert http_source.check(config) is True
    
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.example.com/v1"
    assert kwargs["headers"]["Authorization"] == "Bearer secret"

@patch('httpx.Client.get')
def test_http_source_read_pagination(mock_get, http_source):
    config = {
        "base_url": "https://api.example.com/v1",
        "read_path": "/users",
        "pagination_type": "page",
        "page_param": "p"
    }
    
    # Mocking two pages of results
    def side_effect(url, headers, params):
        page = params.get("p", 1)
        if page == 1:
            req = MagicMock()
            req.url.params = {"p": 1}
            return Response(200, json={"data": [{"id": 1, "name": "Alice"}]}, request=req)
        elif page == 2:
            req = MagicMock()
            req.url.params = {"p": 2}
            return Response(200, json={"data": [{"id": 2, "name": "Bob"}]}, request=req)
        else:
            req = MagicMock()
            return Response(200, json={"data": []}, request=req)

    mock_get.side_effect = side_effect
    
    messages = list(http_source.read(config))
    records = [m.record.data for m in messages if m.type == MessageType.RECORD]
    
    assert len(records) == 2
    assert records[0]["name"] == "Alice"
    assert records[1]["name"] == "Bob"
    assert mock_get.call_count == 3
