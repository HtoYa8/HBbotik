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

from db import init_db, DB_NAME

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("❌ TOKEN не найден в .env файле")

intents = discord.Intents.default()
intents.members = True

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
        print(f"✅ Синхронизировано {len(synced)} команд")
        for cmd in synced:
            print(f"  - {cmd.name}")
    except Exception as e:
        print(f"❌ Ошибка синхронизации команд: {e}")
    
    if not birthday_check.is_running():
        birthday_check.start()
    print(f"✅ Бот запущен как {bot.user}")

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
    print(f"❌ Ошибка команды {interaction.command.name}: {error}")
    if not interaction.response.is_done():
        await interaction.response.send_message(f"❌ Ошибка: {error}", ephemeral=True)

@tasks.loop(time=time(hour=21, minute=0, tzinfo=timezone.utc))
async def birthday_check():
    now = datetime.now(pytz.timezone("Europe/Moscow"))

    if now.hour != 0 or now.minute != 0:
        return

    async with aiosqlite.connect(DB_NAME) as db:
        users = await (await db.execute(
            "SELECT user_id FROM birthdays WHERE day=? AND month=?",
            (now.day, now.month)
        )).fetchall()

        settings = await (await db.execute(
            "SELECT channel_id, hb_message FROM settings"
        )).fetchone()

    if not users or not settings:
        return

    channel = bot.get_channel(settings[0])
    if not channel:
        return

    message = settings[1] or "🎉 С днём рождения, {user}!"

    for (user_id,) in users:
        await channel.send(message.format(user=f"<@{user_id}>"))

async def main():
    async with bot:
        try:
            await bot.load_extension("cogs.birthday_cog")
            print("✅ birthday_cog загружен")
        except Exception as e:
            print(f"❌ Ошибка загрузки birthday_cog: {e}")
        
        try:
            await bot.load_extension("cogs.settings_cog")
            print("✅ settings_cog загружен")
        except Exception as e:
            print(f"❌ Ошибка загрузки settings_cog: {e}")
        
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())