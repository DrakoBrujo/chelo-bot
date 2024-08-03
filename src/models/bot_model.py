from asyncio import Queue

class MusicQueue:
    def __init__(self):
        self.queue = Queue()
        self.current_track = None
        self.playing = False

    async def add_to_queue(self, track):
        await self.queue.put(track)

    async def get_next_track(self):
        if not self.queue.empty():
            self.current_track = await self.queue.get()
            self.playing = True
            return self.current_track
        self.current_track = None
        self.playing = False
        return None

    def is_playing(self):
        return self.playing

    def set_playing(self, playing):
        self.playing = playing

    def get_current_track(self):
        return self.current_track

    async def clear(self):
        while not self.queue.empty():
            await self.queue.get()
        self.current_track = None
        self.playing = False

    def get_queue(self):
        return list(self.queue._queue)

    async def remove_from_queue(self, position):
        queue = self.get_queue()
        if 1 <= position <= len(queue):
            removed_track = queue.pop(position - 1)
            self.queue = Queue()
            for item in queue:
                await self.queue.put(item)
            return removed_track
        return None
