from discord.ext import commands
from botclasses import SilphyBot
import slog


class BaseCog(commands.Cog):
	def __init__(self, bot: SilphyBot):
		self.bot = bot
		slog.log(f"Loaded cog {self.qualified_name}")
