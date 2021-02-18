import traceback

from storage import Database
from discord.ext import commands

import discord
import events
import json
import slog
import sys
import os


class SilphyBot(commands.Bot):
	SETTINGS_FILE = "settings.json"
	TOKEN_KEY = "token"
	SERVER_KEY = "server"
	GATE_CHANNEL_KEY = "gate_channel"
	STAFF_CHANNEL_KEY = "staff_channel"
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
		self.staff_channel_id = 0
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
			await events.gate_check(self, msg)
			return
		elif not self.is_admin(msg.author):
			if msg.channel.id != self.staff_channel_id:
				# If the message is not sent by an admin, and is in the wrong channel, ignore it for now.
				# TODO: Profanity filter
				return
		
		await self.process_commands(message=msg)
	
	async def on_command_error(self, context: commands.Context, exception: commands.CommandError):
		await context.reply("Something went wrong with that command! Make sure you are using it right, or ping Carbon if you are confused x3")
		traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
	
	def create_default_settings(self):
		default_settings = {
			SilphyBot.TOKEN_KEY: "PUT TOKEN HERE",
			SilphyBot.SERVER_KEY: 0,
			SilphyBot.GATE_CHANNEL_KEY: 0,
			SilphyBot.STAFF_CHANNEL_KEY: 0,
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
			
			self.staff_channel_id = self.settings[SilphyBot.STAFF_CHANNEL_KEY]
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
	
	def is_admin(self, user: discord.User):
		return user.id in self.settings[SilphyBot.ADMIN_LIST_KEY]
	
	def load_cogs(self, cogs):
		for cog in cogs:
			self.add_cog(cog)
