import asyncio
from datetime import datetime
from sys import stderr

from discord.ext import commands
from discord import Guild

from MaiConfig import *

class MaiVoiceManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.limit_time = AFK_limit_time
        self.guilds = set()
        self.targets = {}
    
    def open(self, guild: Guild):
        if guild is None:
            return
        
        if guild.id in self.guilds:
            return
        
        self.guilds.add(guild.id)

        voice_channels = guild.voice_channels
        for i in voice_channels:
            self.check_channel(i)
    
    def close(self, guild):
        if guild is None:
            return
        
        if guild.id in self.guilds:
            self.guilds.remove(guild.id)

    def run_on(self, guild):
        return guild.id in self.guilds

    def check_channel(self, channel):
        if channel is None:
            return
        
        members = [m for m in channel.members if not m.bot]

        if len(members) != 1:
            self.remove_target(channel)
            return
        
        self.new_target(channel, channel.guild)
    
    def new_target(self, channel, guild):
        self.targets[channel.id] = datetime.now()
        asyncio.create_task(self.start_timing(channel.id, guild.id))
    
    def remove_target(self, channel):
        if channel.id in self.targets:
            self.targets.pop(channel.id)
    
    async def start_timing(self, id, guild_id):
        def if_need_continue():
            if guild_id in self.guilds:
                if id in self.targets:
                    if (datetime.now() - self.targets[id]).total_seconds() < self.limit_time:
                        return True
            
            return False
        
        while if_need_continue():
            await asyncio.sleep(1)

        if guild_id not in self.guilds:
            if id in self.targets:
                self.targets.pop(id)
            return

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
