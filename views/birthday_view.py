import discord
from discord.ui import View, button
from views.selects import AddBirthdaySelect, RemoveBirthdaySelect
from db import DB_NAME
import aiosqlite

class BirthdayView(View):
    def __init__(self):
        super().__init__(timeout=300)

    @button(label="➕ Добавить ДР", style=discord.ButtonStyle.success)
    async def add(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            "Выберите пользователя:",
            view=AddBirthdaySelect(),
            ephemeral=True
        )

    @button(label="➖ Удалить ДР", style=discord.ButtonStyle.danger)
    async def remove(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            "Выберите пользователя:",
            view=RemoveBirthdaySelect(),
            ephemeral=True
        )

    @button(label="📋 Просмотреть список", style=discord.ButtonStyle.primary)
    async def list(self, interaction: discord.Interaction, _):
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute("SELECT user_id, day, month FROM birthdays")
            rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message("📭 Список пуст", ephemeral=True)
            return

        text = "\n".join(
            f"<@{uid}> — {day:02}.{month:02}"
            for uid, day, month in rows
        )

        await interaction.response.send_message(text, ephemeral=True)
