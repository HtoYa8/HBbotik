import discord
from discord import app_commands
from discord.ext import commands
from services.media_channel_service import get_media_channel_id, set_media_channel, has_media_or_link, extract_text_without_links
from permissions import is_admin
import logging

logger = logging.getLogger("birthdaybot")

class MediaChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setmediachannel")
    async def setmediachannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Установить канал для медиа"""
        if not is_admin(interaction):
            return await interaction.response.send_message("❌ Только администратор", ephemeral=True)

        set_media_channel(channel.id)
        logger.info(f"{interaction.user} установил медиа-канал: {channel.name}")
        await interaction.response.send_message(f"📸 Медиа-канал установлен: {channel.mention}", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Обработка сообщений в медиа-канале"""
        if message.author.bot:
            return

        # Получаем ID медиа-канала
        media_channel_id = get_media_channel_id()
        
        if not media_channel_id or message.channel.id != media_channel_id:
            return

        has_content = has_media_or_link(message)

        # Если нет медиа и ссылок - удаляем сообщение
        if not has_content:
            try:
                await message.delete()
                logger.info(f"Удалено сообщение без медиа/ссылок от {message.author} в {message.channel.name}")
            except (discord.Forbidden, discord.NotFound):
                logger.warning(f"Не удалось удалить сообщение в {message.channel.name}")
            return

        # Если есть медиа или ссылка - создаём ветку
        # Отделяем текст от ссылок
        thread_name = extract_text_without_links(message.content).strip()
        
        # Если текста нет, используем значение по умолчанию
        if not thread_name:
            thread_name = "📸 Медиа"
        
        # Ограничиваем длину названия ветки (максимум 100 символов)
        if len(thread_name) > 100:
            thread_name = thread_name[:97] + "..."

        try:
            thread = await message.create_thread(name=thread_name)
            logger.info(f"Создана ветка '{thread_name}' для медиа от {message.author}")
        except discord.Forbidden:
            logger.warning(f"Не удалось создать ветку в {message.channel.name}")

async def setup(bot):
    await bot.add_cog(MediaChannelCog(bot))
