import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Login to get token
        r = await client.post("/api/v1/auth/login", data={"username": "test@example.com", "password": "password"})
        if r.status_code != 200:
            print("Login failed:", r.text)
            return
        token = r.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get workspaces
        r = await client.get("/api/v1/workspaces", headers=headers)
        if r.status_code != 200:
            print("Get workspaces failed:", r.text)
            return
        workspaces = r.json()
        if not workspaces:
            print("No workspaces")
            return
        
        ws_id = workspaces[0]["id"]
        headers["x-workspace-id"] = ws_id
        
        # 3. Get pipelines
        r = await client.get("/api/v1/pipelines", headers=headers)
        if r.status_code != 200:
            print("Get pipelines failed:", r.text)
            return
        pipelines = r.json()["items"]
        if not pipelines:
            print("No pipelines")
            return
            
        p = pipelines[0]
        
        # 4. Trigger execution
        r = await client.post(f"/api/v1/pipelines/{p['id']}/versions/{p['active_version_id']}/execute", json={}, headers=headers)
        if r.status_code != 202:
            print("Trigger failed:", r.text)
            return
        
        run_id = r.json()["run_id"]
        print("Triggered run_id:", run_id)
        
        # 5. Wait for run to finish
        for i in range(20):
            r = await client.get(f"/api/v1/runs/{run_id}", headers=headers)
            status = r.json()["status"]
            print(f"Status: {status}")
            if status in ["COMPLETED", "FAILED"]:
                print(f"Final error: {r.json().get('error')}")
                break
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
