import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
from db import DB_NAME
from permissions import is_admin
import logging

logger = logging.getLogger("birthdaybot")

class HBMessageModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Текст поздравления")
        self.message_input = discord.ui.TextInput(label="Сообщение", style=discord.TextStyle.paragraph)
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                """
                INSERT INTO settings (guild_id, hb_message)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    hb_message = excluded.hb_message
                """,
                (interaction.guild_id, self.message_input.value)
            )
            await db.commit()
        await interaction.response.send_message("✅ Поздравление сохранено", ephemeral=True)
        logger.info(f"{interaction.user} установил поздравление для пользователей: {self.message_input.value}")

class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hbmessage")
    async def hbmessage(self, interaction: discord.Interaction):
        if not is_admin(interaction):
            await interaction.response.send_message("❌ Только администратор", ephemeral=True)
            return

        await interaction.response.send_modal(HBMessageModal())

    @app_commands.command(name="sethbchannel")
    async def sethbchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not is_admin(interaction):
            return await interaction.response.send_message("❌ Только администратор", ephemeral=True)

        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute(
                """
                INSERT INTO settings (guild_id, channel_id)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    channel_id = excluded.channel_id
                """,
                (interaction.guild_id, channel.id)
            )
            await db.commit()

        logger.info(f"{interaction.user} установил канал для поздравлений: {channel.name}")
        await interaction.response.send_message(f"📢 Канал установлен: {channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SettingsCog(bot))
