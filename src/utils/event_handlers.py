from services.music_player.music_player import MusicPlayer
import discord

music_players = {}

async def on_ready_event(bot):
    print(f'Bot conectado como {bot.user.name}')
    for guild in bot.guilds:
        if guild.id not in music_players:
            music_players[guild.id] = MusicPlayer(bot)
            print(f'Inicializando MusicPlayer para el servidor: {guild.name}')

async def on_guild_join_event(guild, bot):
    if guild.id not in music_players:
        music_players[guild.id] = MusicPlayer(bot)
        print(f'Bot añadido al servidor: {guild.name}')

async def on_guild_remove_event(guild, bot):
    if guild.id in music_players:
        del music_players[guild.id]
        print(f'Bot removido del servidor: {guild.name}')

async def on_voice_state_update_event(bot, member, before, after):
    if member == bot.user and before.channel is not None and after.channel is None:
        channel = discord.utils.get(member.guild.voice_channels, name='General')
        if channel:
            await channel.connect()
