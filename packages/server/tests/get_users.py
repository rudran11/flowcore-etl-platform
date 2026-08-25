import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/flowcore")
    users = await conn.fetch("SELECT email FROM users")
    for u in users:
        print(u['email'])
    await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
