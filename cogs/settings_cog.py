import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
from db import DB_NAME
from permissions import is_admin

class HBMessageModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Текст поздравления")
        self.message_input = discord.ui.TextInput(label="Сообщение", style=discord.TextStyle.paragraph)
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                "REPLACE INTO settings (guild_id, hb_message) VALUES (?, ?)",
                (interaction.guild_id, self.message_input.value)
            )
            await db.commit()
        await interaction.response.send_message("✅ Поздравление сохранено", ephemeral=True)

class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hbmessage")
    async def hbmessage(self, interaction: discord.Interaction):
        if not is_admin(interaction):
            await interaction.response.send_message("❌ Только администратор", ephemeral=True)
            return

        await interaction.response.send_modal(HBMessageModal())

    @app_commands.command(name="setchannel")
    async def setchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not is_admin(interaction):
            return await interaction.response.send_message("❌ Только администратор", ephemeral=True)

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                "REPLACE INTO settings (guild_id, channel_id) VALUES (?, ?)",
                (interaction.guild_id, channel.id)
            )
            await db.commit()

        await interaction.response.send_message(f"📢 Канал установлен: {channel.mention}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(SettingsCog(bot))
