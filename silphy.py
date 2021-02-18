# Silphy Bot v2.0.0a
# By: Carbon

# TODO: Strike Member
# TODO: Random Member
from storage import Database
from discord.ext import commands

from modules.funmod import FunCommands
from modules.adminmod import AdminCommands
from modules.strikecommands import StrikeCommands

from botclasses import SilphyBot

import discord
import logging
import slog

# Constants
VERSION = "2.0.0a"


# client setup
intents = discord.Intents.default()
intents.members = True
silphy_bot = SilphyBot(intents=intents)

	
# Main program
if __name__ == "__main__":
	slog.log("Setting up logger...")
	logging.basicConfig(level=logging.WARNING)
	
	slog.log("Loading settings...")
	silphy_bot.load_settings()
	
	slog.log("Loading cogs...")
	cogs = [AdminCommands(silphy_bot), FunCommands(silphy_bot), StrikeCommands(silphy_bot)]
	silphy_bot.load_cogs(cogs)
	
	slog.log("Starting Client...")
	silphy_bot.run(silphy_bot.settings[SilphyBot.TOKEN_KEY])
