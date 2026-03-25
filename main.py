from sys import stderr

import discord
from discord.ext import commands

from MaiConfig import *
from Mai import Mai
from MaiClock import clocks
from MaiVoiceManager import MaiVoiceManager

import env

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=MaiPrefix, intents=intents)

mai = Mai(bot)

mai_voice_manager = MaiVoiceManager(bot)

@bot.event
async def on_ready():
    print(f'{bot.user} online', file=stderr)

@bot.event
async def on_message(message):
    text = f"{message.content}"
    
    cmd = text.split()

    if len(cmd) <= 0:
        return

    if cmd[0] == MaiPrefix:
        await MaiCmd(cmd, message)
    elif f"{message.author}" == f"{env.master_discord_id}":
        await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    
    if before.channel == after.channel or before.channel == None and after.channel == None:
        return
    
    mai_voice_manager.check_channel(before.channel)
    mai_voice_manager.check_channel(after.channel)

async def MaiCmd(cmd, message):
    if len(cmd) > 1:
        if cmd[1] == "請幫我找人打0AD" and f"{message.author}" == f"{env.master_discord_id}":
            action = bot.get_command("Call0AD")
            ctx = await bot.get_context(message)
            await ctx.invoke(action)
        else:
            await mai.send(message)
    else:
        await mai.send(message)

@bot.command()
async def test(ctx):
    text = f"CMD: {ctx.command.name}\n"
    text += f"Author: {ctx.author}\n"
    text += f"Channel: {ctx.channel}\n"
    text += f"Content: {ctx.message.content}\n"
    text += f"\n"
    await ctx.send(text)

@bot.command()
async def Call0AD(ctx):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name="0AD")

    role_mentions = [member.mention for member in role.members if member is not member.bot]
    
    await ctx.send(f"{' '.join(role_mentions)}\n要不要打0AD")

@bot.command()
async def CheckClock(ctx):
    text = f"{list(clocks.keys())}"
    text = text[1: -1]
    text = text.split(", ")
    text = "\n".join(text)
    
    await ctx.send(f"clock list new:\n{text}")

@bot.command()
async def SeeClock(ctx, *, id):
    if int(id) in clocks:
        clock = clocks[int(id)]
        text = f"clock id: {clock.id}\n"
        text += f"time: {clock.time.tm_hour}:{clock.time.tm_min}\n"
        text += f"date: {clock.date}\n"
        text += f"content: {clock.content}\n"
        text += f"channel_id: {clock.channel_id}\n"

        await ctx.send(text)
    else:
        await ctx.send(f"no clock: {id}")

@bot.command()
async def SwitchVoiceManager(ctx):
    if mai_voice_manager.run_on(ctx.guild):
        mai_voice_manager.close(ctx.guild)
    else:
        mai_voice_manager.open(ctx.guild)
    
    await ctx.send(f"語音頻道管理: {'開啟' if mai_voice_manager.run_on(ctx.guild) else '關閉'}")

if __name__ == "__main__":
    bot.run(f"{env.bot_key}")
