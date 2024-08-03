import discord
import asyncio
import logging

logger = logging.getLogger('audio_player')

class AudioPlayer:
    def __init__(self, ffmpeg_path, ffmpeg_options):
        self.current_vc = None
        self.ffmpeg_path = ffmpeg_path
        self.ffmpeg_options = ffmpeg_options

    def set_voice_client(self, vc):
        self.current_vc = vc

    def is_playing(self):
        return self.current_vc and self.current_vc.is_playing()

    def stop(self):
        if self.current_vc and self.current_vc.is_playing():
            self.current_vc.stop()

    def play(self, url, after):
        if self.current_vc:
            self.current_vc.play(discord.FFmpegPCMAudio(source=url, executable=self.ffmpeg_path, **self.ffmpeg_options), after=after)

    async def disconnect(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.current_vc = None
