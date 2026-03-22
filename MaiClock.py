import asyncio
import time
from datetime import datetime, timezone, timedelta
from sys import stderr

from MaiCMD import *

clocks = {}

class MaiClock:
    def __init__(self):
        self.time_zone = timezone(offset=timedelta(hours=8))
        self.time = time.time()
        self.date = datetime.now(tz=self.time_zone)
        self.content = ""
        self.channel_id = -1
        self._clock_func = None
        self.id = -1
    
    def start(self):
        asyncio.create_task(self._clock())

    def set_id(self, id):
        self.id = id

    def set_time(self, time):
        self.time = time

    def set_date(self, date: datetime):
        self.date = date
        self.date = self.date.replace(tzinfo=self.time_zone)

    def set_content(self, content):
        self.content = content

    def set_channnel_id(self, channel_id):
        self.channel_id = channel_id
    
    def set_clock_func(self, func):
        self._clock_func = func

    async def _clock(self):
        try:
            now = datetime.now(tz=self.time_zone)
            now = now.replace(second=0)

            target_time = self.date
            target_time = target_time.replace(hour=self.time.tm_hour, minute=self.time.tm_min, second=0)

            print(f"{now.strftime('%Y/%m/%d %H:%M')} {target_time.strftime('%Y/%m/%d %H:%M')}", file=stderr)
            while now <= target_time:
                await asyncio.sleep(1)
                now = datetime.now(tz=self.time_zone)
                now.replace(second=0)

        except Exception as e:
            print(f"clock err: {e}", file=stderr)
            print(f"{now.strftime('%Y/%m/%d %H:%M')} {target_time.strftime('%Y/%m/%d %H:%M')}", file=stderr)

        if self._clock_func is not None:
            await self._clock_func(self)
        
        clocks.pop(self.id)

    def get_clock_date(self):
        return f"{self.id} {self.date.year}/{self.date.month}/{self.date.day} {self.time.tm_hour}:{self.time.tm_min} {self.content}"

def new_mai_clock(id, cmd_time, date, content, channel_id, clock_func):
    clock = MaiClock()
    clock.set_id(id)
    clock.set_time(time.strptime(cmd_time, "%H:%M"))
    clock.set_date(datetime.strptime(date, "%Y/%m/%d"))
    clock.set_content(content)
    clock.set_channnel_id(channel_id)
    clock.set_clock_func(clock_func)
    clocks[id] = clock
    clock.start()

    print(clock.get_clock_date(), file=stderr)
