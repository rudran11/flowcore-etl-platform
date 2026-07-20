import asyncio
import asyncpg
import sys

async def check_db():
    passwords = ["postgres", "password", "root", "", "admin"]
    for pwd in passwords:
        try:
            conn = await asyncpg.connect(user="postgres", password=pwd, host="localhost", port=5432)
            print(f"SUCCESS: password is '{pwd}'")
            await conn.close()
            sys.exit(0)
        except Exception as e:
            print(f"FAILED with password '{pwd}': {e}")
            
if __name__ == "__main__":
    asyncio.run(check_db())
