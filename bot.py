import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import logger
from game.game import FNAFDiscordGame

load_dotenv()
TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)

active_games = {}

@bot.event
async def on_ready():
    logger.info(f"{bot.user} is online!")

@bot.command()
async def start(ctx):
    if ctx.author.id in active_games:
        await ctx.send("⚠️You already have a running game!", delete_after=5)
        return
    game = FNAFDiscordGame(ctx.channel, ctx.author, active_games)
    active_games[ctx.author.id] = game
    await game.start_game()
    try:
        await ctx.message.delete()
    except:
        pass

if __name__ == "__main__":
    bot.run(TOKEN)