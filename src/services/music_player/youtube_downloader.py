import yt_dlp as youtube_dl
import asyncio
import re
import tempfile
import os
import shutil

class YouTubeDownloader:
    URL_REGEX = re.compile(r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be|music\.youtube\.com)\/.+$')
    PLAYLIST_REGEX = re.compile(r'^(https?\:\/\/)?(www\.youtube\.com|music\.youtube\.com)\/(playlist\?list=|watch\?v=.+&list=).+$')

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        print(f"Temporary files will be stored in: {self.temp_dir}")
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'source_address': '0.0.0.0'
        }
        
        self.playlist_opts = {
            'extract_flat': 'in_playlist',
            'quiet': True,
            'source_address': '0.0.0.0'
        }

    def is_url(self, query):
        return self.URL_REGEX.match(query) is not None

    def is_playlist(self, query):
        return self.PLAYLIST_REGEX.match(query) is not None

    async def extract_info(self, query, playlist=False):
        loop = asyncio.get_event_loop()
        opts = self.playlist_opts if playlist else self.ydl_opts
        try:
            return await loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(opts).extract_info(query, download=False))
        except Exception as e:
            print(f"Error extracting info from YouTube: {e}")
            return None 

    async def extract_playlist(self, query):
        if 'music.youtube.com' in query:
            query = query.replace('music.youtube.com', 'www.youtube.com')
        return await self.extract_info(query, playlist=True)

    def clean_up(self):
        # Elimina archivos temporales
        shutil.rmtree(self.temp_dir)
        self.temp_dir = tempfile.mkdtemp()
        print(f"Temporary files cleaned up and new temporary directory created: {self.temp_dir}")
