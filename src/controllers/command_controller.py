from services.music_player.music_player import MusicPlayer
from services.gemini_service import generate_playlist
from utils.helpers import get_command_list
import discord
from discord.ext import commands
import json

def setup_commands(bot, music_players):

    @bot.command(name="play")
    async def play(ctx, *, query: str):
        server_id = ctx.guild.id
        if server_id in music_players:
            await music_players[server_id].play_music(ctx, query)
        else:
            await ctx.send("No se pudo encontrar el reproductor de música para este servidor.")

    @bot.command(name="stop")
    async def stop(ctx):
        server_id = ctx.guild.id
        if server_id in music_players:
            await music_players[server_id].stop_music(ctx)
        else:
            await ctx.send("No se pudo encontrar el reproductor de música para este servidor.")

    @bot.command(name="skip")
    async def skip(ctx):
        server_id = ctx.guild.id
        if server_id in music_players:
            await music_players[server_id].skip_music(ctx)
        else:
            await ctx.send("No se pudo encontrar el reproductor de música para este servidor.")

    @bot.command(name="current")
    async def current(ctx):
        server_id = ctx.guild.id
        if server_id in music_players:
            await music_players[server_id].current_track_info(ctx)
        else:
            await ctx.send("No se pudo encontrar el reproductor de música para este servidor.")

    @bot.command(name="pey")
    async def queue(ctx):
        server_id = ctx.guild.id
        if server_id in music_players:
            await music_players[server_id].playlist_info(ctx)
        else:
            await ctx.send("No se pudo encontrar el reproductor de música para este servidor.")

    @bot.command(name="info")
    async def info(ctx):
        commands = get_command_list()
        embed = discord.Embed(
            title="Comandos disponibles",
            color=discord.Color.red()
        )
        for command in commands:
            embed.add_field(name=f"**{command['nombre']}**", value=command['descripcion'], inline=False)
        embed.set_footer(text="**Bot creado por: Wany**")
        await ctx.send(embed=embed)

    @bot.command(name="gnt")
    async def generar(ctx, *, user_prompt: str):
        server_id = ctx.guild.id
        if server_id in music_players:
            await music_players[server_id].generate_playlist(ctx, user_prompt)
        else:
            await ctx.send("No se pudo encontrar el reproductor de música para este servidor.")

    @bot.command(name="remove")
    async def remove(ctx, position: int):
        server_id = ctx.guild.id
        if server_id in music_players:
            await music_players[server_id].remove_track(ctx, position)
        else:
            await ctx.send("No se pudo encontrar el reproductor de música para este servidor.")
