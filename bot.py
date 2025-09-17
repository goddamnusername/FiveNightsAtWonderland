import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import logger
from game.game import FNAFDiscordGame

load_dotenv()

TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=">", intents=intents)

active_games: dict[int, FNAFDiscordGame] = {}


@bot.event
async def on_ready() -> None:
    assert bot.user is not None, "expected bot user to be ready"
    logger.info(f"{bot.user} is online!")


@bot.command()
async def start(ctx: commands.Context[commands.Bot], /) -> None:
    if ctx.author.id in active_games:
        await ctx.send("⚠️You already have a running game!", delete_after=5)
        return

    assert isinstance(ctx.channel, discord.TextChannel), type(ctx.channel)
    assert isinstance(ctx.author, discord.Member), type(ctx.author)
    game = FNAFDiscordGame(ctx.channel, ctx.author, active_games)
    active_games[ctx.author.id] = game
    await game.start_game()

    try:
        await ctx.message.delete()
    except Exception as exc:
        logger.error(f"failed to delete game message: {exc}")


if __name__ == "__main__":
    bot.run(TOKEN)
