import asyncio
import httpx
from flowcore_server.config.settings import settings
from flowcore_server.services.auth import AuthService
from datetime import timedelta
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/flowcore")
    u = await conn.fetchrow("SELECT id, email FROM users LIMIT 1")
    await conn.close()
    
    token = AuthService.create_access_token({"sub": str(u['id'])}, timedelta(minutes=60))
    print("Token ok")
    
    async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
        headers = {"Authorization": f"Bearer {token}", "x-workspace-id": "00000000-0000-0000-0000-000000000000"}
        
        p_id = "df914a55-7f16-4e0f-8f18-76cc3db4f6ee"
        v_id = "1b4add15-4993-4eb1-a009-c22e7db8157c"
        
        print("Triggering execution...")
        r = await client.post(f"/api/v1/pipelines/{p_id}/versions/{v_id}/execute", json={}, headers=headers)
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
                print(f"Error: {r.json().get('error_message')}")
                break
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
