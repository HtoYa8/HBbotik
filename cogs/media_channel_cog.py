import discord
from discord import app_commands
from discord.ext import commands
from services.media_channel_service import (
    add_media_channel, remove_media_channel,
    get_media_channels, has_media_or_link, extract_text_without_links
)
from permissions import is_admin
import logging

logger = logging.getLogger("birthdaybot")


class MediaChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------- команды ----------

    @app_commands.command(name="addmediachannel", description="Добавить медиа-канал")
    async def addmediachannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not is_admin(interaction):
            return await interaction.response.send_message("❌ Только администратор", ephemeral=True)

        add_media_channel(channel.id)
        logger.info(f"{interaction.user} добавил медиа-канал: {channel.name}")
        await interaction.response.send_message(f"📸 {channel.mention} добавлен как медиа-канал", ephemeral=True)

    @app_commands.command(name="removemediachannel", description="Удалить медиа-канал")
    async def removemediachannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not is_admin(interaction):
            return await interaction.response.send_message("❌ Только администратор", ephemeral=True)

        remove_media_channel(channel.id)
        logger.info(f"{interaction.user} удалил медиа-канал: {channel.name}")
        await interaction.response.send_message(f"🗑 {channel.mention} удалён из медиа-каналов", ephemeral=True)

    @app_commands.command(name="listmediachannels", description="Список всех медиа-каналов")
    async def listmediachannels(self, interaction: discord.Interaction):
        channels = get_media_channels()
        if not channels:
            await interaction.response.send_message("❌ Медиа-каналы не заданы", ephemeral=True)
            return

        mentions = [f"<#{cid}>" for cid in channels]
        await interaction.response.send_message("📸 **Медиа-каналы:**\n" + "\n".join(mentions), ephemeral=True)

    # ---------- обработка сообщений ----------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        media_channels = get_media_channels()
        if message.channel.id not in media_channels:
            return

        has_content = has_media_or_link(message)
        if not has_content:
            try:
                await message.delete()
                logger.info(f"Удалено сообщение без медиа/ссылок от {message.author} в {message.channel.name}")
            except (discord.Forbidden, discord.NotFound):
                logger.warning(f"Не удалось удалить сообщение в {message.channel.name}")
            return

        # Создаём ветку
        thread_name = extract_text_without_links(message.content).strip()
        if not thread_name:
            thread_name = "📸 Медиа"
        if len(thread_name) > 100:
            thread_name = thread_name[:97] + "..."

        try:
            await message.create_thread(name=thread_name)
            logger.info(f"Создана ветка '{thread_name}' для медиа от {message.author}")
        except discord.Forbidden:
            logger.warning(f"Не удалось создать ветку в {message.channel.name}")


async def setup(bot):
    await bot.add_cog(MediaChannelCog(bot))
