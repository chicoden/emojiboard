import mysql.connector.aio
import mysql.connector.errors
import asyncio
from config import *

async def main():
    try:
        print("initializing...")
        async with await mysql.connector.aio.connect(**EMO_DB_CONFIG) as db:
            async with await db.cursor() as cursor:
                #await cursor.execute('''
                #''')
                pass
        print("initialization complete.")

    except mysql.connector.errors.Error as error:
        print(f"{EMO_DB_CONFIG["database"]}: connection failed. {error}")

    try:
        print("verifying initialization...")
        async with await mysql.connector.aio.connect(**EMO_DB_CONFIG) as db:
            async with await db.cursor() as cursor:
                await cursor.execute('''
                    SELECT table_name FROM information_schema.tables WHERE table_schema = %s;
                ''', (
                    EMO_DB_CONFIG["database"],
                ))

                table_names = {table_name async for _, (table_name,) in cursor.fetchsets()}
                print(f"tables: {", ".join(table_names)}")
                if table_names == {"foo"}:
                    print("verification success.")
                else:
                    print("verification failure.")

    except mysql.connector.errors.Error as error:
        print(f"{EMO_DB_CONFIG["database"]}: connection failed. {error}")

asyncio.run(main())
