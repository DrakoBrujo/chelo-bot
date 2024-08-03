import sys
import logging
import os
#sys.path.append('C:/Users/Dani/Documents/GitHub/MK-Bot.py/src')
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import discord
from discord.ext import commands
from config.config import Config
from controllers.command_controller import setup_commands
from utils.logger_config import setup_logger
from utils.event_handlers import on_ready_event, on_guild_join_event, on_guild_remove_event, on_voice_state_update_event, music_players

logger = setup_logger()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    await on_ready_event(bot)

@bot.event
async def on_guild_join(guild):
    await on_guild_join_event(guild, bot)

@bot.event
async def on_guild_remove(guild):
    await on_guild_remove_event(guild, bot)

@bot.event
async def on_voice_state_update(member, before, after):
    await on_voice_state_update_event(bot, member, before, after)

setup_commands(bot, music_players)

bot.run(Config.DISCORD_TOKEN)
