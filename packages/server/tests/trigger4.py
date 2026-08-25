import asyncio
import asyncpg
import jwt
import httpx

async def main():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/flowcore")
    u = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
    await conn.close()
    
    token = jwt.encode({"sub": str(u['id'])}, "replace-with-local-secret", algorithm="HS256")
    
    async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
        headers = {"Authorization": f"Bearer {token}"}
        r = await client.get("/api/v1/workspaces", headers=headers)
        if r.status_code != 200:
            print("Failed to get workspaces:", r.status_code, r.text)
            return
            
        workspaces = r.json()
        if not workspaces:
            print("No workspaces")
            return
            
        ws_id = workspaces[0]["id"]
        headers["x-workspace-id"] = ws_id
        
        r = await client.get("/api/v1/pipelines", headers=headers)
        if r.status_code != 200:
            print("Failed to get pipelines:", r.status_code, r.text)
            return
            
        pipelines = r.json()["items"]
        if not pipelines:
            print("No pipelines")
            return
            
        p = pipelines[0]
        r = await client.post(f"/api/v1/pipelines/{p['id']}/versions/{p['active_version_id']}/execute", json={}, headers=headers)
        if r.status_code != 202:
            print("Failed to trigger:", r.text)
            return
            
        run_id = r.json()["run_id"]
        print("Run ID:", run_id)
        
        for i in range(20):
            r = await client.get(f"/api/v1/runs/{run_id}", headers=headers)
            status = r.json()["status"]
            print(f"Status: {status}")
            if status in ["COMPLETED", "FAILED"]:
                print(f"Error: {r.json().get('error')}")
                break
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
