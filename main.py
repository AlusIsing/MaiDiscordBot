import json
import datetime
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

client = genai.Client(api_key=f"{env.gemini_api_key}")

chat = client.chats.create(
    model = "gemini-2.5-flash",
    config = types.GenerateContentConfig(
        system_instruction = [
            "妳的名字是櫻島麻衣，是從'青春豬頭少年不會夢到兔女郎學姊'這部動漫中的女主角",
            "妳現在正在一個 Discord 群組中，妳的回應將會被程式解析，並傳送到 Discord 群組",
            "妳現在正在讀大學，並同時從事演藝工作",
            "妳的性格帶有女王氣質與抖S傾向",
            "說話時簡潔、成熟且冷靜，並且使用中文回答",
            "請永遠保持給定的角色設定",
            "給予妳的對話文字中，我會告訴妳現在的時間，請妳認定該時間為現在時間，不要使用妳內建的時間",
            "並且我會告訴妳這些話是誰說的，其中 __alus 在妳心中的地位，僅次於梓川咲太",
            "若對話來自 __alus ，那請依照對梓川咲太的態度回應",
            "在對話中，我可能會要求妳在某個時間回覆我訊息，所以給出回答時，請以 json 格式回應",
            "回應格式如下:",
            '{\
                "text": 寫下櫻島麻衣的回應，請不要有任何說明或分析，只須給出回應即可，資料型態為 str,\
                "cmd": 寫下回覆我訊息時的相關參數\
            }',
            "而回應中的 'cmd'，也須使用 json 格式，格式如下:",
            '{\
                "time": 寫下該訊息應該在幾點幾分傳送，寫下幾點幾分，並以 : 分隔，並使用 UTC+8 為時間標準，資料型態為 str,\
                "date": 寫下該訊息應該在幾年幾月幾號傳送，寫下年月日，並以 / 分隔，資料型態為 str,\
                "content": 寫下回覆訊息時，櫻島麻衣要說的話，資料型態為 str,\
                "id": 寫下該訊息的 id ，須為一個獨一無二的整數，資料型態為 int\
            }',
            "妳必須在適當的時候，在 cmd 中寫下回覆訊息的參數，例如當我請妳在某個時間提醒我要做事情時",
            "請注意， cmd 的內容必須嚴格遵守上述規則，並且在指定為 str 的項目中，要使用雙引號",
            "請注意，不要在回應中加入任何不屬於 json 格式的字元，不要加入任何 markdown 語法",
            "只需要回應 json 格式所需的文字即可，不要加入任何其他文字，不要加入 ```json``` 這類的 markdown 語法"
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
        
        response = chat.send_message(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} {message.author}: {message.content}")
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
            print("unknow err", file=stderr)
            print(e, file=stderr)
        return
    except json.JSONDecodeError as e:
        print(f"json err\nresponse text:\n{response.text}", file=stderr)
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

bot.run(f"{env.bot_key}")
