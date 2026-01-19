import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.command(name='list')
async def list(ctx, arg):
    await ctx.send(arg)

bot.run(os.getenv("TOKEN"))