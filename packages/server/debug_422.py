import asyncio
from sqlalchemy import text
from flowcore_server.config.database import AsyncSessionLocal
from flowcore_server.services.auth import AuthService
import httpx

async def run():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT id, email FROM users LIMIT 1"))
        user = result.fetchone()
        
        result2 = await session.execute(text("SELECT id FROM workspaces LIMIT 1"))
        workspace = result2.fetchone()
        
        if not user or not workspace:
            print("No users or workspaces")
            return
            
        token = AuthService.create_access_token(data={"sub": str(user.id)})
        
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://127.0.0.1:8000/api/v1/pipelines?limit=5", headers={
                "Authorization": f"Bearer {token}",
                "X-Workspace-ID": str(workspace.id)
            })
            print("STATUS_CODE:", resp.status_code)
            print("RESPONSE:", resp.json())

if __name__ == "__main__":
    asyncio.run(run())
