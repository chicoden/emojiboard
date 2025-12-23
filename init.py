import mysql.connector.aio
import mysql.connector.errors
import asyncio
from config import *

async def main():
    try:
        async with await mysql.connector.aio.connect(**EMO_DB_CONFIG) as db:
            print("initializing...")
            async with await db.cursor() as cursor:
                await cursor.execute('''
                    CREATE TABLE guilds (
                        guild_id BIGINT UNSIGNED,
                        is_tracked BIT
                    );
                    CREATE TABLE tracked_emoji (
                        guild_id BIGINT UNSIGNED,
                        emoji_index BIGINT UNSIGNED
                    );
                    CREATE TABLE emoji (
                        emoji_index BIGINT UNSIGNED AUTO_INCREMENT,
                        is_default BIT,
                        emoji_id BIGINT UNSIGNED,
                        emoji_name VARCHAR(32),
                        primary key (emoji_index)
                    );
                ''')
            print("initialization complete.")

            print("verifying initialization...")
            async with await db.cursor() as cursor:
                await cursor.execute('''
                    SELECT table_name FROM information_schema.tables WHERE table_schema = %s;
                ''', (
                    EMO_DB_CONFIG["database"],
                ))

                table_names = {table_name async for _, (table_name,) in cursor.fetchsets()}
                print(f"tables: {", ".join(table_names)}")
                if table_names == {"guilds", "tracked_emoji", "emoji"}:
                    print("verification success.")
                else:
                    print("verification failure.")

    except mysql.connector.errors.Error as error:
        print(f"{EMO_DB_CONFIG["database"]}: connection failed. {error}")

asyncio.run(main())
