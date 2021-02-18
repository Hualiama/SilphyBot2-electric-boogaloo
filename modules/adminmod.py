from discord.ext import commands
from core import BaseCog
import slog
import sys


class AdminCommands(BaseCog):
	@commands.command(name="shutdown", brief="Shuts down the bot", description="Shuts down the bot")
	async def shutdown(self, ctx: commands.Context):
		if self.bot.is_admin(ctx.author) or self.bot.is_owner(ctx.author):
			await ctx.reply("Shutting down... 💤")
			await self.bot.logout()
			slog.log("Logging out! Goodnight...")
			sys.exit(0)
			
		else:
			slog.warning(f"User {ctx.author.display_name} tried to shut me down! Not today Jose!")
			
	@commands.command(name="gatelock", brief="Prevent users from passing the gate",
	                  description="Toggles the lock on the gate, allowing one to turn off the auto-role feature.")
	async def gate_lock(self, ctx: commands.Context, state: str):
		if self.bot.is_admin(ctx.author) or self.bot.is_owner(ctx.author):
			if state.lower() in ["on", "lock", "locked"]:
				self.bot.gate_lock = True
			elif state.lower() in ["off", "unlock", "unlocked"]:
				self.bot.gate_lock = False
			else:
				await ctx.reply("That's not a valid state! Please enter locked or unlocked o3o")
				return
			
			await ctx.reply(f"Oki, I {'locked' if self.bot.gate_lock else 'unlocked'} the gate o3o")
