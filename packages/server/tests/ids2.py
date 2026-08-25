import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/flowcore")
    u = await conn.fetchrow("SELECT id FROM users LIMIT 1")
    w = await conn.fetchrow("SELECT workspace_id FROM workspace_users WHERE user_id = $1 LIMIT 1", u['id'])
    print(f"Workspace: {w['workspace_id']}")
    
    p = await conn.fetchrow("SELECT id FROM pipelines WHERE workspace_id = $1 LIMIT 1", w['workspace_id'])
    v = await conn.fetchrow("SELECT id FROM pipeline_versions WHERE pipeline_id = $1 ORDER BY created_at DESC LIMIT 1", p['id'])
    
    print(f"Workspace: {w['workspace_id']}")
    print(f"Pipeline: {p['id']}")
    print(f"Version: {v['id']}")
    await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
