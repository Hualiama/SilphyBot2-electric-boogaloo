# Silphy Bot2 v0.0.1a
# By: Carbon and updated by Hualiama

from modules.gatemod import GateCommands
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
VERSION = "0.0.1a"

# Client setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Ensure the bot can read message content

silphy_bot = SilphyBot(intents=intents)

# Main program
if __name__ == "__main__":
    slog.log("Setting up logger...")
    logging.basicConfig(level=logging.INFO)  # Changed to INFO for more general-purpose logging
    
    slog.log("Loading settings...")
    silphy_bot.load_settings()
    
    slog.log("Loading cogs...")
    cogs = [
        AdminCommands(silphy_bot),
        FunCommands(silphy_bot),
        StrikeCommands(silphy_bot),
        GateCommands(silphy_bot)
    ]
    silphy_bot.load_cogs(cogs)

    # Run the bot
    token = silphy_bot.settings.get(SilphyBot.TOKEN_KEY)
    if not token:
        slog.error("No token found in settings file.")
        sys.exit(1)
        
    slog.log("Starting bot...")
    silphy_bot.run(token)
