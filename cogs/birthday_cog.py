import discord
from discord import app_commands
from discord.ext import commands
from views.birthday_view import BirthdayView
from permissions import is_admin

class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="birthday")
    async def birthday(self, interaction: discord.Interaction):
        if not is_admin(interaction):
            await interaction.response.send_message(
                "❌ Только администратор может использовать эту команду",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🎂 Управление днями рождения",
            description="Выберите действие",
            color=discord.Color.purple()
        )

        await interaction.response.send_message(
            embed=embed,
            view=BirthdayView(),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(BirthdayCog(bot))
