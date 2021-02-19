from botclasses import PermissionLevel
from core import BaseCog
from discord.ext import commands
from storage import StrikeConsts

import discord


class StrikeCommands(BaseCog):
	@commands.command(name="strike", brief="[MT] Adds a strike for a user", description="Adds a strike for a user. Reason must be in quotation marks.")
	async def add_strike(self, ctx: commands.Context, user: discord.User, severity: str, reason: str):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.TRIAL_MOD):
			return
		
		sev_score = StrikeConsts.get_severity(severity)
		
		if sev_score == StrikeConsts.INVALID_SEVERITY:
			await ctx.reply("That's not a valid severity!")
			return
		
		if len(reason) > StrikeConsts.STRIKE_REASON_CHAR_LIMIT:
			await ctx.reply(f"The reason must be under 200 characters, your reason is {len(reason)} characters!")
			return
		
		strikes = self.bot.database.add_strike(user, ctx.message.author, reason, sev_score)
		
		if strikes < 0:
			await ctx.reply(
				f"Something went wrong, my records say {user.mention} has {strikes} strikes! Tell Carbon to check the database.")
		elif strikes >= 3:
			await ctx.reply(f"User {user.mention} has {strikes} strikes, they must now be banned >:3c")
		else:
			await ctx.reply(f"Strike added for {user.mention}, they now have {strikes} strikes!")
	
	@commands.command(name='forgive', brief='[M] Removes a strike for a user', description='Removes strike strike_number for the user.')
	async def remove_strike(self, ctx: commands.Context, user: discord.User, strike_number: int):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.MODERATOR):
			return
		
		new_strikes = self.bot.database.remove_strike(user, strike_number)
		
		if new_strikes == -1:
			await ctx.reply(f"{user.mention} isn't in my records!")
		elif new_strikes == -2:
			await ctx.reply(f"{user.mention} doesn't have that many strikes!")
		elif new_strikes == -3:
			await ctx.reply("Please enter a position between 1 and 3!")
		else:
			await ctx.reply(f"{user.mention} now has {new_strikes} strike{'s' if new_strikes != 1 else ''} x3")
	
	@commands.command(name='view', brief='[MT] Displays strike data for user', description='Displays the strike data for a user')
	async def view_user(self, ctx: commands.Context, user: discord.User):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.TRIAL_MOD):
			return
		
		user_stats = self.bot.database.get_user_stats(user)
		
		if len(user_stats) == 0:
			await ctx.reply(f"{user.mention} is not in my records uwu")
			return
		
		panel = discord.Embed(title=f"{user.display_name}#{user.discriminator}", color=0xffd70f)
		panel.set_author(name=f"Entry for {user.display_name}", icon_url=self.bot.user.avatar_url)
		panel.set_thumbnail(url=user.avatar_url)
		
		st = ["Strike One ", "Strike Two ", "Ban "]
		dt = ["Reason", "Date", "Moderator", "Severity"]
		
		for stage, ind in zip(StrikeConsts.STAGES, [0, 1, 2]):
			for data, jnd in zip(StrikeConsts.STRIKE_DATA, [0, 1, 2, 3]):
				inline = jnd != 3
				
				val = user_stats[stage + data]
				valstr = str(val) if val is not None else "None"
				
				if jnd == 2 and val is not None:
					valstr = ctx.guild.get_member(val).mention
					
				panel.add_field(name=f"{st[ind] if jnd == 0 else ''}{dt[jnd]}", value=valstr, inline=inline)
		
		await ctx.channel.send(embed=panel)
	
	@commands.command(name='wipe', brief='[A] Removes a user from the strike database.', description='Removes a user from the strike database.')
	async def clear_user(self, ctx: commands.context, user: discord.User):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.ADMIN):
			return
		
		result = self.bot.database.remove_user(user)
		
		if result:
			await ctx.reply(f"I wiped {user.mention} from the records o3o")
		else:
			await ctx.reply(f"{user.mention} isn't in the records!")
