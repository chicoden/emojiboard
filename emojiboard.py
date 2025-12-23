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

class EmojiRegistrationRecord:
    is_default:   bool
    is_animated:  bool
    emoji_id:     int
    emoji_name:   str
    emoji_weight: int

    def __init__(self, row: Tuple[int, int, int, str, int]):
        self.is_default   = bool(row[0])
        self.is_animated  = bool(row[1])
        self.emoji_id     = row[2]
        self.emoji_name   = row[3]
        self.emoji_weight = row[4]

    def __repr__(self):
        return "<EmojiRegistrationRecord"              \
            f" is_default={repr(self.is_default)}"     \
            f" is_animated={repr(self.is_animated)}"   \
            f" emoji_id={repr(self.emoji_id)}"         \
            f" emoji_name={repr(self.emoji_name)}"     \
            f" emoji_weight={repr(self.emoji_weight)}" \
        ">"

    def matches(self, emoji: discord.PartialEmoji | discord.Emoji | str) -> bool:
        match emoji:
            case discord.Emoji() | discord.PartialEmoji():
                return not self.is_default and self.emoji_id == emoji.id

            case str():
                return self.is_default and self.emoji_name == emoji

            case _:
                return False

async def post_leaderboard(guild: discord.Guild, tracked_emoji: List[EmojiRegistrationRecord], start_timestamp: datetime.datetime):
    self_member = guild.get_member(client.user.id)

    leaderboard_channel = discord.utils.get(guild.text_channels, name="emojiboard")
    if leaderboard_channel is None:
        log.info(f"creating leaderboard channel for guild {guild.name}")
        leaderboard_channel = await guild.create_text_channel(name="emojiboard", topic="Emoji leaderboard channel")

    log.info(f"creating leaderboard for guild {guild.name}")
    winner_message: Optional[discord.Message] = None
    winner_relevant_reactions: List[discord.Reaction] = []
    winner_score = 0
    for channel in guild.text_channels:
        channel_permissions = channel.permissions_for(self_member)
        if not channel_permissions.read_message_history:
            continue # avert our eyes

        async for message in channel.history(after=start_timestamp):
            score = 0
            relevant_reactions: List[discord.Reaction] = []
            for reaction in message.reactions:
                for record in tracked_emoji:
                    if record.matches(reaction.emoji):
                        score += reaction.count * record.emoji_weight
                        relevant_reactions.append(reaction)
                        break

            if score > 0 and score >= winner_score:
                winner_message = message
                winner_relevant_reactions = relevant_reactions
                winner_score = score

    if winner_message is not None:
        relevant_reaction_counts = ", ".join(f"{reaction.count}{reaction.emoji}" for reaction in winner_relevant_reactions)
        await leaderboard_channel.send(f"{winner_message.author.mention} wins with {relevant_reaction_counts}")
        await winner_message.forward(leaderboard_channel)

    else:
        await leaderboard_channel.send(f"No winners {BotEmoji.KEKKED_SADGE}")

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
            log.info(f"{EMO_DB_CONFIG["database"]}: connected")
            async with asyncio.TaskGroup() as per_guild:
                log.info("creating leaderboard tasks")
                start_timestamp = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=24)
                async with (
                    await db.cursor() as guild_cursor,
                    await db.cursor() as emoji_cursor
                ):
                    await guild_cursor.execute("SELECT guild_id, is_tracked FROM guilds")
                    for guild_id, is_tracked in await guild_cursor.fetchall():
                        log.info(f"guild id {guild_id}, is tracked {is_tracked}")

                        guild = client.get_guild(guild_id)
                        if guild is None:
                            # purge from database?
                            log.debug(f"guild id {guild_id} not found in client guilds")
                            continue

                        if is_tracked:
                            await emoji_cursor.execute('''
                                SELECT emoji.is_default, emoji.is_animated, emoji.emoji_id, emoji.emoji_name, tracked_emoji.emoji_weight
                                    FROM emoji INNER JOIN tracked_emoji ON tracked_emoji.emoji_index = emoji.emoji_index
                                    WHERE tracked_emoji.guild_id = %s;
                            ''', (guild_id,))
                            tracked_emoji = [EmojiRegistrationRecord(row) for row in await emoji_cursor.fetchall()]
                            per_guild.create_task(post_leaderboard(guild, tracked_emoji, start_timestamp))
                            log.info(f"leaderboard task created for guild {guild.name}")

    except mysql.connector.errors.Error as error:
        log.error(f"{EMO_DB_CONFIG["database"]}: connection failed. {error}")

@client.event
async def on_ready():
    if not task_post_leaderboards.is_running(): # avoid starting an already running task (yes, this can happen, and it raises an exception)
        task_post_leaderboards.start()

    log.info("ready")

client.run(DISCORD_BOT_TOKEN)
