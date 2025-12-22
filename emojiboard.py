import discord
from discord.ext import tasks
from mysql.connector.aio import connect
import asyncio
import datetime
import re
from config import *

client = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(client)

class BotEmoji:
    KEKW = "<:kekw:1311365036660363378>"
    KEKKED_SADGE = "<:kekked_sadge:1439802912745197670>"

@tree.command(name="saykekw", description="Say kekw")
async def say_kekw(interaction):
    async with interaction.channel.typing():
        await asyncio.sleep(2)
        await interaction.response.send_message(BotEmoji.KEKW)

vowels = re.compile("[aeiouAEIOU]+")
@tree.command(name="mask_vowels", description="Hides vowels")
async def mask_vowels(interaction, message: str):
    await interaction.response.send_message(
        vowels.sub(lambda match: f"||{match.group()}||", message)
    )

@tasks.loop(hours=24)
async def task_make_leaderboard():
    start_timestamp = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=24)
    for guild in client.guilds:
        bot_member = guild.get_member(client.user.id)

        emojiboard_channel = discord.utils.get(guild.text_channels, name="emojiboard")
        if emojiboard_channel is None:
            print(f"Creating topic channel for guild {guild.name}")
            emojiboard_channel = await guild.create_text_channel(name="emojiboard", topic="Dedicated emojiboard channel")

        winner = None
        winning_score = 0
        for channel in guild.text_channels:
            channel_permissions = channel.permissions_for(bot_member)
            if not channel_permissions.read_message_history:
                continue

            async for message in channel.history(after=start_timestamp):
                score = 0
                for reaction in message.reactions:
                    emoji = reaction.emoji
                    if type(emoji) is discord.Emoji and emoji.name.lower() == "kekw":
                        score = max(score, reaction.count)

                if score > 0 and score >= winning_score:
                    winner = message
                    winning_score = score

        if winner is not None:
            await emojiboard_channel.send(f"{winner.author.mention} wins with {winning_score} kekw reactions")
            await winner.forward(emojiboard_channel)

        else:
            await emojiboard_channel.send(f"No winners {BotEmoji.KEKKED_SADGE}")

@client.event
async def on_ready():
    if not task_make_leaderboard.is_running():
        task_make_leaderboard.start()

    print("Ready")

client.run(DISCORD_BOT_TOKEN)
