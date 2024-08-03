import discord
import logging
import asyncio
import json
from discord.ext import commands
from .queue_manager import QueueManager
from .audio_player import AudioPlayer
from .youtube_downloader import YouTubeDownloader
from utils.discord_bot_utils import send_current_track_info, send_playlist_info
from services.gemini_service import generate_playlist as generate_gemini_playlist
import imageio_ffmpeg as ffmpeg

logger = logging.getLogger('music_player')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='music_player.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(console_handler)

ffmpeg_path = ffmpeg.get_ffmpeg_exe()
ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.queue_manager = QueueManager()
        self.audio_player = AudioPlayer(ffmpeg_path, ffmpeg_options)
        self.downloader = YouTubeDownloader()
        self.playing_now = False
        self.current_tasks = []

    def create_embed(self, title, url, thumbnail, author):
        embed = discord.Embed(
            title="Agrega3",
            description=f'[{title}]({url})',
            colour=0x2c76dd,
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Requested by: {str(author)}', icon_url=author.display_avatar.url)
        return embed
#aca
    async def extract_and_queue_video(self, ctx, query, search=True):
        try:
            info = await self.downloader.extract_info(query if not search else f"ytsearch:{query}")
            if 'entries' in info:
                info = info['entries'][0]
            url = info['url']
            title = info['title']
            thumbnail = info['thumbnail']
            duration = info.get('duration', 0)
            await self.queue_manager.add_to_queue((url, title, duration))
            return title, url, thumbnail
        except Exception as e:
            logger.error(f"Error extracting or queuing video: {e}")
            await ctx.send(f"Error extracting video information: {e}")
            return None

    async def ensure_voice_connection(self, ctx):
        if not ctx.voice_client:
            return await ctx.author.voice.channel.connect()
        return ctx.voice_client

    async def play_music(self, ctx, query):
        if not ctx.author.voice:
            return await ctx.send("Tenes que estar conectado a un canal de voz.")

        vc = await self.ensure_voice_connection(ctx)
        self.audio_player.set_voice_client(vc)

        try:
            if self.downloader.is_playlist(query):
                playlist_info = await self.downloader.extract_playlist(query)
                entries = playlist_info.get('entries', [])

                if entries:
                    total_songs = len(entries)
                    first_entry = entries.pop(0)
                    first_video_url = f"https://www.youtube.com/watch?v={first_entry['id']}"
                    title, url, thumbnail = await self.extract_and_queue_video(ctx, first_video_url)
                    embed = self.create_embed(title, url, thumbnail, ctx.author)
                    await ctx.send(embed=embed)

                    if not self.queue_manager.is_playing():
                        await self.play_next(ctx)

                    asyncio.create_task(self.add_remaining_songs(ctx, entries))
            else:
                title, url, thumbnail = await self.extract_and_queue_video(ctx, query, search=not self.downloader.is_url(query))
                embed = self.create_embed(title, url, thumbnail, ctx.author)
                await ctx.send(embed=embed)
                if not self.queue_manager.is_playing():
                    await self.play_next(ctx)
        except Exception as e:
            logger.error(f"Error extracting or playing URL: {e}")
            await ctx.send(f"Error: {e}")

    async def add_remaining_songs(self, ctx, entries):
        song_titles = []
        for entry in entries:
            if 'id' in entry:
                video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                task = asyncio.create_task(self.process_song(ctx, video_url))
                self.current_tasks.append(task)
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Tarea para el video {video_url} cancelada.")
                    return
                except Exception as e:
                    logger.error(f"Error processing song {video_url}: {e}")

    async def process_song(self, ctx, video_url):
        try:
            video_info = await self.downloader.extract_info(video_url)
            url = video_info['url']
            title = video_info['title']
            duration = video_info.get('duration', 0)
            await self.queue_manager.add_to_queue((url, title, duration))
            queue_size = self.queue_manager.get_queue_size()
            logger.debug(f"URL extraída: {url}")
            logger.info(f"Añadido a la peylist: {title} (Posición {queue_size})")
            return title
        except asyncio.CancelledError:
            logger.info(f"Tarea de proceso de canción cancelada: {video_url}")
            raise
        except Exception as e:
            logger.error(f"Error processing song: {e}")
            raise

    async def generate_playlist(self, ctx, user_prompt):
        embed_generating = discord.Embed(
            title="Generando Peylist...",
            description="🎵 Generando la peylist, por favor espera... 🎵",
            color=discord.Color.blue()
        )
        generating_message = await ctx.send(embed=embed_generating)
        
        response_text = generate_gemini_playlist(user_prompt)
        logger.debug(f"Response from Gemini: {response_text}")

        if response_text.startswith("```json") and response_text.endswith("```"):
            response_text = response_text[7:-3].strip()

        try:
            playlist = json.loads(response_text)
            logger.debug(f"Parsed playlist: {playlist}")

            if isinstance(playlist, list):
                first_song = True
                for song in playlist:
                    title = song.get("title")
                    artist = song.get("artist")

                    if title and artist:
                        search_query = f"{title} {artist}"
                        if first_song:
                            await self.extract_and_queue_video(ctx, search_query, search=not self.downloader.is_url(search_query))
                            if not ctx.voice_client:
                                channel = ctx.author.voice.channel
                                vc = await channel.connect()
                                self.audio_player.set_voice_client(vc)
                            await self.play_next(ctx)
                            first_song = False
                        else:
                            task = asyncio.create_task(self.extract_and_queue_video(ctx, search_query, search=True))
                            self.current_tasks.append(task)
                            try:
                                await task
                            except asyncio.CancelledError:
                                logger.info(f"Tarea para {search_query} cancelada.")
                                return
                            except Exception as e:
                                logger.error(f"Error processing song {search_query}: {e}")

                embed_completed = discord.Embed(
                    title="Peylist Generada",
                    description=f"🎵 Peylist generada y añadida con {len(playlist)} canciones! 🎵",
                    color=discord.Color.green()
                )
                await generating_message.edit(embed=embed_completed)

                await self.playlist_info(ctx)
            else:
                embed_error = discord.Embed(
                    title="Error",
                    description="❌ No se pudo generar una peylist válida. Inténtalo de nuevo.",
                    color=discord.Color.red()
                )
                await generating_message.edit(embed=embed_error)
                logger.error("No se pudo generar una playlist válida.")
        except json.JSONDecodeError as e:
            embed_error = discord.Embed(
                title="Error",
                description=f"Parece que hubo un error al generar la peylist",
                color=discord.Color.red()
            )
            await generating_message.edit(embed=embed_error)
            logger.error(f"JSON Decode Error: {e}")

    async def play_next(self, ctx):
        if self.audio_player.is_playing():
            logger.info("Ya hay una canción reproduciéndose, esperando a que termine.")
            return

        track = await self.queue_manager.get_next_track()
        if track and len(track) == 3:
            url, title, duration = track
            logger.info(f"Iniciando la reproducción de: {title}")
            
            embed = discord.Embed(
                title="Reproduciendo ahora",
                description=f"[{title}]({url})",
                colour=0x2c76dd,
            )
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{url.split('=')[-1]}/hqdefault.jpg")
            embed.set_footer(text=f"Duración: {duration // 60}:{duration % 60:02d}")

            await ctx.send(embed=embed)

            self.queue_manager.set_playing(True)
            self.audio_player.play(url, after=lambda e: asyncio.run_coroutine_threadsafe(self.after_playing(ctx, e), ctx.bot.loop))
            self.playing_now = True
        else:
            self.queue_manager.set_playing(False)
            logger.info("La cola de reproducción está vacía.")
            self.playing_now = False
            asyncio.create_task(self.disconnect_after_timeout(ctx))

    async def after_playing(self, ctx, error):
        if error:
            logger.error(f"Error durante la reproducción: {error}")
            embed = discord.Embed(
                title="Error",
                description=f"Error durante la reproducción: {error}",
                colour=0xdf1141,
            )
            await ctx.send(embed=embed)
        self.playing_now = False
        await self.play_next(ctx)

    async def skip_music(self, ctx):
        if self.audio_player.is_playing():
            logger.info("Saltando la canción actual.")
            self.audio_player.stop()
            self.queue_manager.set_playing(False)
            embed = discord.Embed(
                title="Skipea3",
                description="Skipea3",
                colour=0xdf1141,
            )
            await ctx.send(embed=embed)

    async def stop_music(self, ctx):
        if self.audio_player.is_playing():
            logger.info("Deteniendo la música y vaciando la playlist.")
            self.audio_player.stop()
            self.playing_now = False

        for task in self.current_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Tarea {task} cancelada exitosamente.")
            except Exception as e:
                logger.error(f"Error cancelando la tarea {task}: {e}")

        self.current_tasks = []

        await self.queue_manager.clear_queue()
        self.queue_manager.set_playing(False)
        embed = discord.Embed(
            title="Stopped",
            description="La música ha sido detenida y la playlist ha sido vaciada.",
            colour=0xdf1141,
        )
        await ctx.send(embed=embed)
        
        await self.audio_player.disconnect(ctx)

    async def current_track_info(self, ctx):
        current_track = self.queue_manager.get_current_track()
        if current_track:
            url, title, duration = current_track
            logger.info(f"Mostrando información de la canción: {title}")

            embed = discord.Embed(
                title="Reproduciendo ahora",
                description=f"[{title}]({url})",
                colour=0x2c76dd,
            )
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{url.split('=')[-1]}/hqdefault.jpg")
            embed.set_footer(text=f"Duración: {duration // 60}:{duration % 60:02d}")

            await ctx.send(embed=embed)
        else:
            await ctx.send("No hay ninguna canción en reproducción actualmente.")

    async def playlist_info(self, ctx):
        queue = self.queue_manager.get_queue()
        if not queue:
            await ctx.send("No hay canciones en la cola de reproducción actualmente.")
            return

        items_per_page = 10
        total_pages = (len(queue) + items_per_page - 1) // items_per_page
        current_page = 0

        def generate_page(page):
            start = page * items_per_page
            end = start + items_per_page
            tracks = queue[start:end]
            total_duration = sum(track[2] for track in queue)
            
            description = ""
            for i, track in enumerate(tracks, start=start + 1):
                url, title, duration = track
                truncated_url = url[:100] + "..." if len(url) > 100 else url
                description += f"{i}. [{title}]({truncated_url}) - {duration // 60}:{duration % 60:02d}\n"
            
            embed = discord.Embed(
                title=f"Canciones en la peylist ({len(queue)}):",
                description=description,
                color=discord.Color.blue()
            )
            embed.add_field(name="Duración total restante", value=f"{total_duration // 60}m {total_duration % 60}s", inline=False)
            embed.set_footer(text=f"Página {page + 1}/{total_pages}")
            return embed

        embed = generate_page(current_page)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('⬅️')
        await msg.add_reaction('➡️')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️'] and reaction.message.id == msg.id

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                if str(reaction.emoji) == '⬅️' and current_page > 0:
                    current_page -= 1
                    await msg.edit(embed=generate_page(current_page))
                    await msg.remove_reaction(reaction, user)
                elif str(reaction.emoji) == '➡️' and current_page < total_pages - 1:
                    current_page += 1
                    await msg.edit(embed=generate_page(current_page))
                    await msg.remove_reaction(reaction, user)
                else:
                    await msg.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                break

    async def remove_track(self, ctx, position):
        current_track = self.queue_manager.get_current_track()
        removed_track = await self.queue_manager.remove_from_queue(position)
        
        embed = discord.Embed(color=discord.Color.red())
        
        if removed_track:
            embed.title = "🎵 Canción Removida"
            embed.description = f"La canción '{removed_track[1]}' ha sido removida de la posición {position}."
            logger.info(f"Canción '{removed_track[1]}' removida de la posición {position}.")
            
            if current_track and current_track[1] == removed_track[1]:
                await self.skip_music(ctx)
        else:
            embed.title = "❌ Error"
            embed.description = f"No se pudo remover la canción en la posición {position}. Verifica el número e inténtalo de nuevo."
            logger.error(f"No se pudo remover la canción en la posición {position}.")
        
        await ctx.send(embed=embed)

    async def disconnect_after_timeout(self, ctx):
        await asyncio.sleep(180)  
        if not self.queue_manager.is_playing() and not self.playing_now:
            if ctx.voice_client:
                await ctx.voice_client.disconnect()

            await self.queue_manager.clear_queue()

            self.downloader.clean_up()

            embed = discord.Embed(
                title="",
                description="Ahora me ves y ahora me vooooy 😢",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logger.info("Desconectado del canal de voz por inactividad.")

            self.queue_manager = QueueManager()
            self.downloader = YouTubeDownloader()
            self.playing_now = False
            
        logger.info("Recursos limpiados correctamente.")


