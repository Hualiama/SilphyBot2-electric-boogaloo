from discord.ext import commands
from utils import is_number
from core import BaseCog
import discord
import random


class FunCommands(BaseCog):
	@commands.command(name="raffle", brief="Selects a random member", description="Select a random member. If role is specified, selects only those with that role.")
	@commands.has_permissions(manage_messages=True)
	async def random_member(self, ctx: commands.Context, role: str = ""):
		if role != "" and not is_number(role):
			await ctx.reply("Please enter the role ID, or leave it blank to look through everyone x3")
		else:
			role_id = int(role) if role != "" else -1
			role_obj = ctx.guild.get_role(role_id)
			
			users = list(filter(lambda x: (role_obj is None) or (role_obj in x.roles), ctx.guild.members))
			target = random.choice(users)
			
			await ctx.reply(f"I choose: {target.mention}")
	
	@commands.command(name="say", brief="Sends a message in a channel", description="Sends [text] in [channel].")
	@commands.has_permissions(manage_messages=True)
	async def message_channel(self, ctx: commands.Context, channel: discord.TextChannel, *, text):
		perms: discord.Permissions = ctx.guild.get_member(ctx.me.id).permissions_in(channel)
		
		if not (perms.send_messages and perms.view_channel):
			await ctx.reply("I can't send messages there x3")
			return

		await channel.send(text)
		
	@commands.command(name="whisper", brief="Sends a private message to a user", description="Sends [text] tp [user] in a direct message.")
	@commands.has_permissions(manage_messages=True)
	async def dm_user(self, ctx: commands.Context, user: discord.Member, *, text):
		try:
			await user.send(text)
		except discord.HTTPException:
			await ctx.reply("I can't DM that user! They either blocked me, or have direct messages turned off!")

	@commands.command(name="ping")
	@commands.has_permissions(manage_messages=True)
	async def ping(self, ctx: commands.Context):
		await ctx.reply("Pong!")
