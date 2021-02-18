from discord.ext import commands
from core import BaseCog
import slog
import sys


class AdminCommands(BaseCog):
	@commands.command(name="shutdown", brief="Shuts down the bot", description="Shuts down the bot")
	@commands.has_permissions(administrator=True)
	async def shutdown(self, ctx: commands.Context):
		if self.bot.is_admin(ctx.author) or self.bot.is_owner(ctx.author):
			await ctx.reply("Shutting down... 💤")
			await self.bot.logout()
			slog.log("Logging out! Goodnight...")
			sys.exit(0)
			
		else:
			slog.warning(f"User {ctx.author.display_name} tried to shut me down! Not today Jose!")
