import discord
from discord.ext import commands

import env

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} online')

@bot.event
async def on_message(message):
    if message.author != f"{env.master_discord_id}":
        return
    
    await bot.process_commands(message)

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
