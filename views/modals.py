import discord
from discord.ui import Modal, TextInput
import aiosqlite
from db import DB_NAME

class AddBirthdayModal(Modal):
    def __init__(self, user_id):
        super().__init__(title="Добавить день рождения")
        self.user_id = user_id

        self.day = TextInput(label="День", placeholder="1-31")
        self.month = TextInput(label="Месяц", placeholder="1-12")

        self.add_item(self.day)
        self.add_item(self.month)

    async def on_submit(self, interaction: discord.Interaction):
        day = int(self.day.value)
        month = int(self.month.value)

        if not (1 <= day <= 31 and 1 <= month <= 12):
            await interaction.response.send_message("❌ Некорректная дата", ephemeral=True)
            return

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                "REPLACE INTO birthdays VALUES (?, ?, ?)",
                (self.user_id, day, month)
            )
            await db.commit()

        await interaction.response.send_message("✅ День рождения сохранён", ephemeral=True)
