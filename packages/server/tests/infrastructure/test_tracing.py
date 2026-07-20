from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from flowcore_server.middleware.tracing import request_id_var, TracingMiddleware

def test_tracing_middleware():
    app = FastAPI()
    app.add_middleware(TracingMiddleware)
    
    @app.get("/test")
    def test_route():
        return {"req_id": request_id_var.get()}
        
    client = TestClient(app)
    
    # Test generation of UUID when no header is present
    response = client.get("/test")
    assert response.status_code == 200
    req_id = response.json()["req_id"]
    assert req_id != ""
    assert response.headers["X-Request-ID"] == req_id
    
    # Test preserving existing header
    existing_id = "test-1234-uuid"
    response2 = client.get("/test", headers={"X-Request-ID": existing_id})
    assert response2.status_code == 200
    assert response2.json()["req_id"] == existing_id
    assert response2.headers["X-Request-ID"] == existing_id
