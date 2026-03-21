import asyncio
import time
import datetime

clocks = {}

class MaiClock:
    def __init__(self):
        self.time = time.time()
        self.date = datetime.datetime.now().date()
        self.content = ""
        self.channel_id = -1
        self._clock_func = None
        self.id = -1
    
    def start(self):
        self._clock()

    def set_time(self, time):
        self.time = time

    def set_date(self, date):
        self.date = date

    def set_content(self, content):
        self.content = content

    def set_channnel_id(self, channel_id):
        self.channel_id = channel_id
    
    def set_clock_func(self, func):
        self._clock_func = func

    async def _clock(self):
        while self.time <= time.time():
            await asyncio.sleep(1)

        if self._clock_func is not None:
            await self._clock_func(self)
        
        clocks.pop(self.id)

def new_mai_clock(id, time, date, content, channel_id, clock_func):
    clock = MaiClock()
    clock.set_time(time)
    clock.set_date(date)
    clock.set_content(content)
    clock.set_channnel_id(channel_id)
    clock.set_clock_func(clock_func)
    clocks[id] = clock
    clock.start()
