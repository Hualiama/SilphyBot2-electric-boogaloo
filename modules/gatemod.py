from discord.ext import commands
from core import BaseCog
from botclasses import PermissionLevel

import slog


class GateCommands(BaseCog):
	@commands.command(name="gatelock", brief="[A] Prevent users from passing the gate",
	                  description="Toggles the lock on the gate, allowing one to turn off the auto-role feature.")
	async def gate_lock(self, ctx: commands.Context, state: str):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.ADMIN):
			return
			
		if state.lower() in ["on", "lock", "locked"]:
			self.bot.gate_lock = True
		elif state.lower() in ["off", "unlock", "unlocked"]:
			self.bot.gate_lock = False
		else:
			await ctx.reply("That's not a valid state! Please enter locked or unlocked o3o")
			return
		
		await ctx.reply(f"Oki, I {'locked' if self.bot.gate_lock else 'unlocked'} the gate o3o")
			
	@commands.command(name="getcode", brief="[MT] Gets the current gate password")
	async def get_gate_code(self, ctx: commands.Context):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.TRIAL_MOD):
			return
		
		await ctx.reply(f"Gate password is: {self.bot.gate_password}")
		
	@commands.command(name="setcode", brief="[M] Sets the gate password", description="Sets the gate password to code. Password must be in quotes.")
	async def set_gate_code(self, ctx: commands.Context, code: str):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.MODERATOR):
			return
		
		slog.log(f"Setting gate code to '{code}'...")
		self.bot.gate_password = code
		self.bot.save_settings()
		
		await ctx.reply(f"Oki, I set the code to: {code}")
