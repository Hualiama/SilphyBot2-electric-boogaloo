from core import BaseCog
from discord.ext import commands
from storage import StrikeConsts

import discord


class StrikeCommands(BaseCog):
	@commands.command(name="addstrike")
	async def add_strike(self, ctx: commands.Context, user: discord.User, severity: str, reason: str):
		sev_score = StrikeConsts.get_severity(severity)
		
		if sev_score == StrikeConsts.INVALID_SEVERITY:
			await ctx.reply("That's not a valid severity!")
			return
		
		strikes = self.bot.database.add_strike(user, ctx.message.author, reason, sev_score)
		
		if strikes < 0:
			await ctx.reply(f"Something went wrong, my records say {user.mention} has {strikes} strikes! Tell Carbon to check the database.")
		elif strikes >= 3:
			await ctx.reply(f"User {user.mention} has {strikes} strikes, they must now be banned >:3c")
		else:
			await ctx.reply(f"Strike added for {user.mention}, they now have {strikes} strikes!")
			
	@commands.command(name='forgive')
	async def remove_strike(self, ctx: commands.Context, user: discord.User, strike_number: int):
		new_strikes = self.bot.database.remove_strike(user, strike_number)
		
		if new_strikes == -1:
			await ctx.reply(f"{user.mention} isn't in my records!")
		elif new_strikes == -2:
			await ctx.reply(f"{user.mention} doesn't have that many strikes!")
		elif new_strikes == -3:
			await ctx.reply("Please enter a position between 1 and 3!")
		else:
			await ctx.reply(f"{user.mention} now has {new_strikes} strike{'s' if new_strikes != 1 else ''} x3")
			
	@commands.command(name='wipe')
	@commands.has_permissions(administrator=True)
	async def clear_user(self, ctx: commands.context, user: discord.User):
		result = self.bot.database.remove_user(user)
		
		if result:
			await ctx.reply(f"I wiped {user.mention} from the records o3o")
		else:
			await ctx.reply(f"{user.mention} isn't in the records!")
