import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.command(name='list')
async def list(ctx, arg):
    await ctx.send(arg)

bot.run('MTQ2MTgwNTk2MjY2NTkyMjgwMg.GIlW3D.Guht9lfLd1hmCF20TP-rUpxa-kZs0pModoJDbM')