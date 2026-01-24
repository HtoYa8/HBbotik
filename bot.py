import os
import discord
import asyncio
import aiosqlite
import pytz

import logging
from discord.ext import commands, tasks
from datetime import datetime
from dotenv import load_dotenv
from datetime import time, timezone
from services.birthday_service import send_birthday_messages

from db import init_db, DB_NAME

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("❌ TOKEN не найден в .env файле")
    
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("birthdaybot")

@bot.event
async def on_ready():
    await init_db()
    try:
        synced = await bot.tree.sync()
        logging.info(f"✅ Синхронизировано {len(synced)} команд")
        for cmd in synced:
            print(f"  - {cmd.name}")
    except Exception as e:
        logging.error(f"❌ Ошибка синхронизации команд: {e}")
    
    if not birthday_check.is_running():
        birthday_check.start()
    logging.info(f"✅ Бот запущен как {bot.user}")

@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command):
    user = interaction.user
    guild = interaction.guild.name if interaction.guild else "DM"
    channel = interaction.channel.name if interaction.channel else "DM"

    logger.info(
        f"{user} ({user.id}) использовал /{command.name} "
        f"| Сервер: {guild} | Канал: {channel}"
    )


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    logging.error(f"❌ Ошибка команды {interaction.command.name}: {error}")
    if not interaction.response.is_done():
        await interaction.response.send_message(f"❌ Ошибка: {error}", ephemeral=True)


@tasks.loop(time=time(hour=21, minute=0, tzinfo=timezone.utc))
async def birthday_check():
    now = datetime.now(pytz.timezone("Europe/Moscow"))
    
    if not bot.guilds:
        return

    guild = bot.guilds[0]

    await send_birthday_messages(
        bot,
        DB_NAME,
        guild.id,
        now
    )

async def main():
    async with bot:
        try:
            await bot.load_extension("cogs.birthday_cog")
            logging.info("✅ birthday_cog загружен")
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки birthday_cog: {e}")
        
        try:
            await bot.load_extension("cogs.settings_cog")
            logging.info("✅ settings_cog загружен")
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки settings_cog: {e}")

        try:
            await bot.load_extension("cogs.media_channel_cog")
            logging.info("✅ media_channel_cog загружен")
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки media_channel_cog: {e}")

        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())