from discord.ext import commands

import slog


class BaseCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		slog.log(f"Loaded cog {self.qualified_name}")
