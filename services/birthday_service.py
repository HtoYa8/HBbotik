from datetime import datetime
import pytz
import aiosqlite
import logging

logger = logging.getLogger("birthdaybot")

async def send_birthday_messages(bot, db_name, guild_id, date: datetime):
    async with aiosqlite.connect(db_name) as db:
        users = await (await db.execute(
            "SELECT user_id FROM birthdays WHERE day=? AND month=?",
            (date.day, date.month)
        )).fetchall()

        settings = await (await db.execute(
            "SELECT channel_id, hb_message FROM settings WHERE guild_id = ?",
            (guild_id,)
        )).fetchone()

        logger.info("Настройки из БД:", settings)

        if not users or not settings:
            return False

        channel = bot.get_channel(settings[0])
        if not channel:
            return False

        message = settings[1] or "🎉 С днём рождения, {user}!"

        for (user_id,) in users:
            await channel.send(
                message.format(user=f"<@{user_id}>")
            )
            logger.info(f"Бот поздравил пользователя {user_id}")

    return True
