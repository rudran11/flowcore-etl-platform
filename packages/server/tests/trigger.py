import httpx
import asyncio

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000", headers={"Authorization": "Bearer mock-token"}) as client:
        r = await client.get("/api/v1/workspaces")
        print("Workspaces:", r.status_code, r.text)
        
        # We need a workspace ID to set in header
        # But wait, there is no API to get workspaces yet?
        # Let's see if pipelines endpoint returns anything
        r = await client.post("/api/v1/pipelines", json={})
        print(r.status_code)
if __name__ == '__main__': asyncio.run(main())
