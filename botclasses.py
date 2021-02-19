import traceback

from storage import Database
from discord.ext import commands

import discord
import events
import json
import slog
import sys
import os


class PermissionLevel:
	SILENCED = -1
	UNTRUSTED = 0
	MEMBER = 1
	TRUSTED = 2
	TRIAL_MOD = 3
	MODERATOR = 4
	ADMIN = 5
	SERVER_OWNER = 6
	BOT_OWNER = 100
	

class SilphyBot(commands.Bot):
	SETTINGS_FILE = "settings.json"
	TOKEN_KEY = "token"
	SERVER_KEY = "server"
	GATE_CHANNEL_KEY = "gate_channel"
	STAFF_CHANNEL_KEY = "staff_channels"
	GATE_PASSWORD_KEY = "passphrase"
	ADMIN_LIST_KEY = "admins"
	STAFF_ROLE_KEY = "mod_role"
	MEMBER_ROLE_KEY = "member_role"
	TRAINER_MOD_ROLE_KEY = "training_role"
	DATABASE_NAME_KEY = "database_name"
	DATABASE_USER_KEY = "database_user"
	DATABASE_PASS_KEY = "database_pass"
	DATABASE_PORT_KEY = "database_port"
	DATABASE_HOST_KEY = "database_host"
	
	def __init__(self, **options):
		super().__init__("!", **options)
		self.settings = None
		self.staff_channel_ids = []
		self.gate_channel_id = 0
		self.staff_role_id = 0
		self.staff_training_role_id = 0
		self.member_role_id = 0
		self.server_id = 0
		self.gate_password = ""
		self.admin_list = []
		self.database_name = ""
		self.database_user = ""
		self.database: Database = Database("", "", "")
		self.gate_lock = False
	
	async def on_ready(self):
		slog.log("Ready!")
		slog.log(f"Logged in as {self.user.display_name}")
	
	async def on_message(self, msg: discord.Message):
		if msg.author.bot or msg.guild is None:
			return
		
		if msg.guild.id != self.server_id:
			return
		
		if msg.channel.id == self.gate_channel_id:
			# Process gate message
			if self.gate_lock:
				slog.warning(f"User {msg.author.display_name} tried to get through the gate, but the gate is locked!")
			else:
				await events.gate_check(self, msg)
				
			return
		elif not self.permission_gate(msg.author, PermissionLevel.ADMIN):
			if msg.channel.id not in self.staff_channel_ids:
				# If the message is not sent by an admin, and is in the wrong channel, ignore it for now.
				# TODO: Profanity filter
				return
		
		await self.process_commands(message=msg)
	
	async def on_command_error(self, context: commands.Context, exception: commands.CommandError):
		if issubclass(type(exception), commands.CommandNotFound):
			return
		
		await context.reply("Something went wrong with that command! Make sure you are using it right, or ping Carbon if you are confused x3")
		traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
	
	def create_default_settings(self):
		default_settings = {
			SilphyBot.TOKEN_KEY: "PUT TOKEN HERE",
			SilphyBot.SERVER_KEY: 0,
			SilphyBot.GATE_CHANNEL_KEY: 0,
			SilphyBot.STAFF_CHANNEL_KEY: [],
			SilphyBot.GATE_PASSWORD_KEY: "toy pianos",
			SilphyBot.ADMIN_LIST_KEY: [],
			SilphyBot.STAFF_ROLE_KEY: 0,
			SilphyBot.TRAINER_MOD_ROLE_KEY: 0,
			SilphyBot.MEMBER_ROLE_KEY: 0,
			SilphyBot.DATABASE_NAME_KEY: "DATABASE NAME",
			SilphyBot.DATABASE_USER_KEY: "LOGIN USER",
			SilphyBot.DATABASE_PASS_KEY: "PUT PASSWORD HERE",
			SilphyBot.DATABASE_PORT_KEY: "5432",
			SilphyBot.DATABASE_HOST_KEY: "localhost"
		}
		
		self.settings = default_settings
		self.save_settings()
		
		slog.info("Default settings file created, please update it.")
		input("Press enter to continue.")
		sys.exit(0)
	
	def save_settings(self):
		slog.log("Saving settings...")
		
		with open(SilphyBot.SETTINGS_FILE, 'w') as f:
			json.dump(self.settings, f, indent=4)
		
		slog.log("Saved settings.")
	
	def load_settings(self):
		slog.log("Loading settings...")
		
		if not os.path.exists(SilphyBot.SETTINGS_FILE):
			self.create_default_settings()
		else:
			with open(SilphyBot.SETTINGS_FILE) as sf:
				self.settings = json.load(sf)
			
			self.staff_channel_ids = self.settings[SilphyBot.STAFF_CHANNEL_KEY]
			self.gate_channel_id = self.settings[SilphyBot.GATE_CHANNEL_KEY]
			self.staff_role_id = self.settings[SilphyBot.STAFF_ROLE_KEY]
			self.staff_training_role_id = self.settings[SilphyBot.TRAINER_MOD_ROLE_KEY]
			self.member_role_id = self.settings[SilphyBot.MEMBER_ROLE_KEY]
			self.server_id = self.settings[SilphyBot.SERVER_KEY]
			self.gate_password = self.settings[SilphyBot.GATE_PASSWORD_KEY]
			self.admin_list = self.settings[SilphyBot.ADMIN_LIST_KEY]
			self.database_user = self.settings[SilphyBot.DATABASE_USER_KEY]
			self.database_name = self.settings[SilphyBot.DATABASE_NAME_KEY]
			self.database = Database(self.database_user,
			                         self.settings[SilphyBot.DATABASE_PASS_KEY],
			                         self.database_name,
			                         self.settings[SilphyBot.DATABASE_PORT_KEY],
			                         self.settings[SilphyBot.DATABASE_HOST_KEY])
		
		slog.log("Settings loaded.")
	
	def load_cogs(self, cogs):
		for cog in cogs:
			self.add_cog(cog)

	def get_perm_level(self, user: discord.Member) -> int:
		role_ids = set([x.id for x in user.roles])
		
		if self.owner_id == user.id:
			return PermissionLevel.BOT_OWNER
		elif user.guild.owner_id == user.id:
			return PermissionLevel.SERVER_OWNER
		elif user.id in self.admin_list:
			return PermissionLevel.ADMIN
		elif self.staff_role_id in role_ids:
			return PermissionLevel.MODERATOR
		elif self.staff_training_role_id in role_ids:
			return PermissionLevel.TRIAL_MOD
		elif self.member_role_id in role_ids:
			return PermissionLevel.MEMBER
		else:
			return PermissionLevel.UNTRUSTED
	
	def get_perm_level_name(self, user: discord.Member) -> str:
		lvl = self.get_perm_level(user)
		
		lvls = {
			PermissionLevel.SILENCED: "Silenced",
			PermissionLevel.UNTRUSTED: "Untrusted",
			PermissionLevel.MEMBER: "Member",
			PermissionLevel.TRUSTED: "Trusted",
			PermissionLevel.TRIAL_MOD: "Mod in Training",
			PermissionLevel.MODERATOR: "Moderator",
			PermissionLevel.ADMIN: "Admin",
			PermissionLevel.SERVER_OWNER: "Server Owner",
			PermissionLevel.BOT_OWNER: "Bot Owner"
		}
		
		return lvls[lvl]
		
	def permission_gate(self, user: discord.Member, level: int) -> bool:
		"""Determines if user meets the specified permission level.
		
		:param user: The user to test
		:param level: The minimum PermissionLevel the user must
		:returns: True if the user meets or exceeds level, False otherwise
		"""
		return self.get_perm_level(user) >= level
