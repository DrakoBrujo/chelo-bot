from models.bot_model import MusicQueue

class QueueManager:
    def __init__(self):
        self.music_queue = MusicQueue()

    async def add_to_queue(self, track):
        await self.music_queue.add_to_queue(track)

    async def get_next_track(self):
        return await self.music_queue.get_next_track()

    def is_playing(self):
        return self.music_queue.is_playing()

    def set_playing(self, state):
        self.music_queue.set_playing(state)

    async def clear_queue(self):
        await self.music_queue.clear()

    def get_queue_size(self):
        return self.music_queue.queue.qsize()

    def get_queue(self):
        return self.music_queue.get_queue()

    def get_current_track(self):
        return self.music_queue.get_current_track()

    async def remove_from_queue(self, position):
        return await self.music_queue.remove_from_queue(position)

    async def clear(self):
        while not self.music_queue.queue.empty():
            await self.music_queue.queue.get()
        self.music_queue.current_track = None
        self.music_queue.playing = False
