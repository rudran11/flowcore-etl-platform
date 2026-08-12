import requests

def test_api():
    # Login
    resp = requests.post("http://127.0.0.1:8000/api/v1/auth/login", data={
        "username": "admin@flowcore.io",
        "password": "admin"
    })
    if "access_token" not in resp.json():
        print("Auth failed:", resp.text)
        return
        
    token = resp.json()["access_token"]
    
    # Get workspace ID
    # Actually from the logs we saw options preflight for workspace: "1b589417-3d12-42de-8e50-9d3329747d21"
    # Or we can just get /workspaces
    ws_resp = requests.get("http://127.0.0.1:8000/api/v1/workspaces", headers={"Authorization": f"Bearer {token}"})
    workspace_id = ws_resp.json()[0]["id"]
    
    # Hit pipelines
    pipelines_resp = requests.get("http://127.0.0.1:8000/api/v1/pipelines?limit=5", headers={
        "Authorization": f"Bearer {token}",
        "X-Workspace-ID": workspace_id
    })
    
    print("STATUS:", pipelines_resp.status_code)
    print("BODY:", pipelines_resp.json())

if __name__ == "__main__":
    test_api()
