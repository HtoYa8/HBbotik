import discord
from discord.ui import View, UserSelect
from views.modals import AddBirthdayModal
from db import DB_NAME
import aiosqlite

class AddBirthdaySelect(View):
    @discord.ui.select(cls=UserSelect, placeholder="Выберите пользователя")
    async def select(self, interaction: discord.Interaction, select: UserSelect):
        user = select.values[0]
        await interaction.response.send_modal(AddBirthdayModal(user.id))


class RemoveBirthdaySelect(View):
    @discord.ui.select(cls=UserSelect, placeholder="Выберите пользователя")
    async def select(self, interaction: discord.Interaction, select: UserSelect):
        user = select.values[0]

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("DELETE FROM birthdays WHERE user_id = ?", (user.id,))
            await db.commit()

        await interaction.response.send_message(
            f"🗑️ День рождения {user.mention} удалён",
            ephemeral=True
        )
