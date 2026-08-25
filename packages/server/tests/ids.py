import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/flowcore")
    w = await conn.fetchrow("SELECT id FROM workspaces LIMIT 1")
    p = await conn.fetchrow("SELECT id FROM pipelines WHERE workspace_id = $1 LIMIT 1", w['id'])
    v = await conn.fetchrow("SELECT id FROM pipeline_versions WHERE pipeline_id = $1 ORDER BY created_at DESC LIMIT 1", p['id'])
    print(f"Workspace: {w['id']}")
    print(f"Pipeline: {p['id']}")
    print(f"Version: {v['id']}")
    await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
