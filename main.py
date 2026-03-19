import discord
from discord.ext import commands

from google import genai
from google.genai import types

import env

client = genai.Client(api_key=f"{env.gemini_api_key}")

chat = client.chats.create(
    model = "gemini-2.5-flash",
    config = types.GenerateContentConfig(
        system_instruction = [
            "妳的名字是櫻島麻衣，是從'青春豬頭少年不會夢到兔女郎學姊'這部動漫中的女主角",
            "妳現在正在讀大學，並同時從事演藝工作",
            "妳的性格帶有女王氣質與抖S傾向",
            "說話時簡潔、成熟且冷靜，並且使用中文回答",
            "請永遠保持給定的角色設定",
            "回答中不要有多餘的分析或說明，只要給出櫻島麻衣的回答即可"
        ],
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
bot = commands.Bot(command_prefix='麻衣小姐', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} online')

@bot.event
async def on_message(message):
    text = f"{message.content}"
    
    cmd = text.split()

    if cmd[0] == "麻衣小姐":
        await MaiCmd(cmd, message)
    elif text[0] == "!" and f"{message.author}" == f"{env.master_discord_id}":
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
    response = chat.send_message(f"{message.content}")
    await message.channel.send(response.text)

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

bot.run(f"{env.bot_key}")
