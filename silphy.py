# Silphy Bot v2.0.0a
# By: Carbon

# TODO: Strike Member
# TODO: Random Member
from storage import Database
from discord.ext import commands

from modules.adminmod import AdminCommands
from modules.funmod import FunCommands
from modules.strikecommands import StrikeCommands

import discord
import logging
import events
import json
import slog
import sys
import os

# Constants
VERSION = "2.0.0a"


# Classes
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
	
	def __init__(self, database_user="", database="", **options):
		super().__init__("!", **options)
		self.settings = None
		self.staff_channel_id = 0
		self.gate_channel_id = 0
		self.staff_role_id = 0
		self.staff_training_role_id = 0
		self.member_role_id = 0
		self.server_id = 0
		self.gate_password = "toy pianos"
		self.admin_list = []
		# self.database = Database(database_user, database)
		
	def create_default_settings(self):
		default_settings = {
			"token": "PUT TOKEN HERE",
			"server": 0,
			"gate_channel": 0,
			"staff_channel": 0,
			"passphrase": "toy pianos",
			"admins": [],
			"mod_role": 0,
			"training_role": 0,
			"member_role": 0
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
			
		slog.log("Settings loaded.")
	
	def is_admin(self, user: discord.User):
		return user.id in self.settings[SilphyBot.ADMIN_LIST_KEY]
	
	def load_cogs(self):
		self.add_cog(FunCommands(self))
		self.add_cog(StrikeCommands(self))
		self.add_cog(AdminCommands(self))


# client setup
intents = discord.Intents.default()
intents.members = True
silphy_bot = SilphyBot(intents=intents)


# handlers
@silphy_bot.event
async def on_ready():
	slog.log("Ready!")
	slog.log(f"Logged in as {silphy_bot.user.display_name}")


@silphy_bot.event
async def on_message(msg: discord.Message):
	if msg.author.bot or msg.guild is None:
		return
	
	if msg.guild.id != silphy_bot.server_id:
		return
	
	if msg.channel.id == silphy_bot.gate_channel_id:
		# Process gate message
		await events.gate_check(silphy_bot, msg)
		return
	elif not silphy_bot.is_admin(msg.author):
		if msg.channel.id != silphy_bot.staff_channel_id:
			# If the message is not sent by an admin, and is in the wrong channel, ignore it for now.
			# TODO: Profanity filter
			return
	
	await silphy_bot.process_commands(message=msg)
		
	
# Main program
if __name__ == "__main__":
	slog.log("Setting up logger...")
	logging.basicConfig(level=logging.WARNING)
	
	slog.log("Loading settings...")
	silphy_bot.load_settings()
	
	slog.log("Loading cogs...")
	silphy_bot.load_cogs()
	
	slog.log("Starting Client...")
	silphy_bot.run(silphy_bot.settings[SilphyBot.TOKEN_KEY])
