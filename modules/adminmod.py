from discord.ext import commands
from botclasses import PermissionLevel
from core import BaseCog
from datetime import datetime
from os import path, makedirs

import discord
import slog
import json


class AdminCommands(BaseCog):
	@commands.command(name="shutdown", brief="Shuts down the bot", description="Shuts down the bot")
	async def shutdown(self, ctx: commands.Context):
		if self.bot.permission_gate(ctx.author, PermissionLevel.ADMIN):
			await ctx.reply("Shutting down... 💤")
			await self.bot.logout()
			slog.log("Logging out! Goodnight...")
		else:
			slog.warning(f"User {ctx.author.display_name} tried to shut me down! Not today Jose!")

	@commands.command(name="fixroles", brief="gives spectral pirates to anyone with a role")
	async def fix_roles(self, ctx: commands.Context):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.ADMIN):
			return
		
		mem_role = ctx.guild.get_role(self.bot.member_role_id)
		user: discord.Member
		
		to_role = []
		
		for user in ctx.guild.members:
			# Note: This is >1 not >0 because @everyone is always in the role list.
			if len(user.roles) > 1 and mem_role not in user.roles:
				to_role.append(user)
				
		if len(to_role) == 0:
			await ctx.channel.send("There's nobody to give the role to!")
			return
		
		await ctx.reply(f"Granting member role to {len(to_role)} {'people' if len(to_role) != 1 else 'person'}...")
		
		granted = 0
		
		for user in to_role:
			slog.info(f"Fixing roles for {user.display_name}... {granted}/{len(to_role)} ({round(granted/len(to_role) * 100, 2)}%)")
			
		slog.info("Done fixing roles!")
		await ctx.channel.send("Done! x3")
	
	@commands.command(name="admin", brief="Grants a user admin perms with Silphy")
	async def add_admin(self, ctx: commands.Context, user: discord.User):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.ADMIN):
			return
		
		slog.warning(f"Added user {user.display_name}#{user.discriminator} as an admin.")
		self.bot.admin_list.append(user.id)
		self.bot.save_settings()
		
		await ctx.reply(f"{user.mention} is now an Admin!")
	
	@commands.command(name="snapshot")
	async def take_snapshot(self, ctx: commands.Context):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.ADMIN):
			return
		
		role_map = {}
		user_map = {}
		
		await ctx.reply("Oki, taking a snapshot of things, this might take a while!")
		
		# Gather roles data
		role: discord.Role
		for role in ctx.guild.roles:
			role_map[role.id] = role.name
		
		# Gather member data
		member: discord.Member
		for member in ctx.guild.members:
			rl = []
			
			for role in member.roles:
				rl.append(role.id)
			
			user_map[member.id] = rl
		
		# Save file
		folder_path = path.join(path.dirname(__file__), "..", "snapshots")
		
		if not path.exists(folder_path):
			makedirs(folder_path)
			slog.warning("Snapshot folder does not exist, creating it now...")
		
		filename = path.abspath(path.join(folder_path, f"snapshot_{ctx.guild.name}_AT_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"))
		
		with open(filename, 'w+') as fp:
			json.dump([role_map, user_map], fp, indent=4)
			slog.warning(f"Snapshot saved at {filename}")
			
		await ctx.channel.send("Snapshot saved o3o")

	@commands.command(name="permlvl", brief="Shows the permission level of a user")
	async def perm_level(self, ctx: commands.Context, user: discord.Member):
		if not self.bot.permission_gate(ctx.author, PermissionLevel.TRIAL_MOD):
			return
		
		await ctx.reply(f"{user.display_name} has permission level {self.bot.get_perm_level_name(user)}!")
