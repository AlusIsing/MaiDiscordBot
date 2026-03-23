import json
from datetime import datetime, timezone, timedelta
from sys import stderr

import discord
from discord.ext import commands

from google import genai
from google.genai import types
from google.genai.errors import APIError

import MaiClock
from MaiClock import MaiClock, clocks, new_mai_clock

from MaiCMD import *

import env

time_taiwan = timezone(offset=timedelta(hours=8))

client = genai.Client(api_key=f"{env.gemini_api_key}")

chat = client.chats.create(
    model = UseModel,
    config = types.GenerateContentConfig(
        system_instruction = [
            SystemPrompt
        ],
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        temperature = 0.7,
        max_output_tokens = 500,
        safety_settings = [
            types.SafetySetting(
                category = types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold = types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            )
        ]
    )
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=MaiPrefix, intents=intents)

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

async def MaiCmd(cmd, message):
    if len(cmd) > 1:
        if cmd[1] == "請幫我找人打0AD" and f"{message.author}" == f"{env.master_discord_id}":
            action = bot.get_command("Call0AD")
            ctx = await bot.get_context(message)
            await ctx.invoke(action)
        else:
            await MaiChat(message)
    else:
        await MaiChat(message)

async def MaiChat(message):
    try:
        if len(chat.get_history()) > MaxChatHistoryAmount * 2:
            chat.history = chat.get_history()[:-MaxChatHistoryAmount * 2]

        message_no_prefix = list(str(message.content).split(" "))[1:]
        message_no_prefix = " ".join(message_no_prefix)

        print(message_no_prefix)
        
        response = chat.send_message(f"{datetime.now(tz=time_taiwan).strftime('%Y-%m-%d %H:%M')} {message.author}: {message_no_prefix}")
        response_json = json.loads(response.text)
        
        response_text = response_json["text"]

        if "cmd" in response_json:
            response_cmd = response_json["cmd"]
            SolveCmd(response_cmd, message.channel.id)

        await message.channel.send(response_text)
    except APIError as e:
        if e.code == 429:
            await message.channel.send("我累了，有什麼話等下再說。")
        else:
            print("unknow API err", file=stderr)
            print(e, file=stderr)
        return
    except json.JSONDecodeError as e:
        print(f"json err\nresponse text:\n{response.text}", file=stderr)
        return
    except Exception as e:
        print(f"unknow err: {e}", file=stderr)
        return

@bot.command()
async def GetAnno(ctx):
    await ctx.send("""hier ist ein discord bot""")

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

async def clock_func(clock: MaiClock):
    channel = bot.get_channel(clock.channel_id)
    await channel.send(f"{clock.content}")

def SolveCmd(cmd, channel_id):
    if cmd:
        new_mai_clock(
            int(cmd["id"]),
            cmd["time"],
            cmd["date"],
            cmd["content"],
            channel_id,
            clock_func
        )

if __name__ == "__main__":
    bot.run(f"{env.bot_key}")
