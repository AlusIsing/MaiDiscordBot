import asyncio
from datetime import datetime
from sys import stderr

from discord.ext import commands

from MaiCMD import *

class MaiVoiceManager:
    def __init__(self, bot: commands.Bot):
        self.running = False
        self.bot = bot
        self.limit_time = AFK_limit_time
        self.targets = {}
    
    def open(self):
        self.running = True
    
    def close(self):
        self.running = False

    def check_channel(self, channel):
        if channel is None:
            return
        
        if not self.running:
            return
        
        members = [m for m in channel.members if not m.bot]

        if len(members) != 1:
            self.remove_target(channel)
            return
        
        self.new_target(channel)
    
    def new_target(self, channel):
        self.targets[channel.id] = datetime.now()
        asyncio.create_task(self.start_timing(channel.id))
    
    def remove_target(self, channel):
        if channel.id in self.targets:
            self.targets.pop(channel.id)
    
    async def start_timing(self, id):
        def if_need_continue(id):
            if id in self.targets:
                if (datetime.now() - self.targets[id]).total_seconds() < self.limit_time:
                    return True
            
            return False
        
        while if_need_continue(id) and self.running:
            await asyncio.sleep(1)

        if id in self.targets:
            await self.remove_member(id)
            if id in self.targets:
                self.targets.pop(id)
    
    async def remove_member(self, id):
        channel = self.bot.get_channel(id)
        members = [m for m in channel.members if not m.bot]
        
        if len(members) == 1:
            await members[0].move_to(None)
        else:
            print(f"channel should not remove member: {channel.name}", file=stderr)
