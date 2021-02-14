from discord.ext import commands
from utils import is_number
from core import BaseCog
import random


class FunCommands(BaseCog):
	@commands.command(name="raffle", brief="Selects a random member", description="Select a random member. If role is specified, selects only those with that role.")
	async def random_member(self, ctx: commands.Context, role: str = ""):
		if role != "" and not is_number(role):
			await ctx.reply("Please enter the role ID, or leave it blank to look through everyone x3")
		else:
			role_id = int(role) if role != "" else -1
			role_obj = ctx.guild.get_role(role_id)
			
			users = list(filter(lambda x: (role_obj is None) or (role_obj in x.roles), ctx.guild.members))
			target = random.choice(users)
			
			await ctx.reply(f"I choose: {target.mention}")
