import discord
from discord.ext import tasks
import mysql.connector.aio
import mysql.connector.errors
import asyncio
import datetime
import logging
import re
from typing import *
from config import *

type EmojiDescriptor = Tuple[bool, int, str]

log = logging.getLogger("emojiboard")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt="[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)

client = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client)

class BotEmoji:
    KEKW = "<:kekw:1311365036660363378>"
    KEKKED_SADGE = "<:kekked_sadge:1439802912745197670>"

async def post_leaderboard(guild: discord.Guild, tracked_emoji: List[EmojiDescriptor], start_timestamp: datetime.datetime):
    log.debug(f"posting leaderboard in guild {guild.name}")

@tree.command(name="saykekw", description="Say kekw")
async def say_kekw(interaction: discord.Interaction):
    async with interaction.channel.typing():
        await asyncio.sleep(2)
        await interaction.response.send_message(BotEmoji.KEKW)

vowels = re.compile("[aeiouAEIOU]+")
@tree.command(name="mask_vowels", description="Hides vowels")
async def mask_vowels(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(
        vowels.sub(lambda match: f"||{match.group()}||", message)
    )

@tasks.loop(hours=24)
async def task_post_leaderboards():
    try:
        async with await mysql.connector.aio.connect(**EMO_DB_CONFIG) as db:
            async with asyncio.TaskGroup() as per_guild:
                start_timestamp = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=24)
                async with (
                    await db.cursor() as guild_cursor,
                    await db.cursor() as emoji_cursor
                ):
                    await guild_cursor.execute("SELECT guild_id, is_tracked FROM guilds")
                    async for _, (guild_id, is_tracked) in guild_cursor.fetchsets():
                        guild = client.get_guild(guild_id)
                        if guild is None:
                            # purge from database?
                            continue

                        if is_tracked:
                            await emoji_cursor.execute('''
                                SELECT emoji.is_default, emoji.emoji_id, emoji.emoji_name FROM emoji
                                    INNER JOIN tracked_emoji ON tracked_emoji.emoji_index = emoji.emoji_index
                                    WHERE tracked_emoji.guild_id = %i;
                            ''', (guild_id,))
                            tracked_emoji = await emoji_cursor.fetchall()
                            per_guild.create_task(post_leaderboard(guild, tracked_emoji, start_timestamp))

    except mysql.connector.errors.Error as error:
        log.error(f"{EMO_DB_CONFIG["database"]}: connection failed. {error}")

# @tasks.loop(hours=24)
# async def task_make_leaderboard():
#     start_timestamp = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=24)
#     for guild in client.guilds:
#         bot_member = guild.get_member(client.user.id)
#         emojiboard_channel = discord.utils.get(guild.text_channels, name="emojiboard")
#         if emojiboard_channel is None:
#             log.info(f"creating topic channel for guild {guild.name}")
#             emojiboard_channel = await guild.create_text_channel(name="emojiboard", topic="Dedicated emojiboard channel")
#         winner = None
#         winning_score = 0
#         for channel in guild.text_channels:
#             channel_permissions = channel.permissions_for(bot_member)
#             if not channel_permissions.read_message_history:
#                 continue
#             async for message in channel.history(after=start_timestamp):
#                 score = 0
#                 for reaction in message.reactions:
#                     emoji = reaction.emoji
#                     if type(emoji) is discord.Emoji and emoji.name.lower() == "kekw":
#                         score = max(score, reaction.count)
#                 if score > 0 and score >= winning_score:
#                     winner = message
#                     winning_score = score
#         if winner is not None:
#             await emojiboard_channel.send(f"{winner.author.mention} wins with {winning_score} kekw reactions")
#             await winner.forward(emojiboard_channel)
#         else:
#             await emojiboard_channel.send(f"No winners {BotEmoji.KEKKED_SADGE}")

@client.event
async def on_ready():
    #if not task_post_leaderboards.is_running(): # avoid starting an already running task (yes, this can happen, and it raises an exception)
    #    task_post_leaderboards.start()

    log.info("ready")

client.run(DISCORD_BOT_TOKEN)
