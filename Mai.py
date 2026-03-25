from sys import stderr
import json
from datetime import datetime, timezone, timedelta

from discord.ext import commands

from google import genai
from google.genai import types
from google.genai.errors import APIError

import env
from MaiClock import new_mai_clock
from MaiConfig import *

class Mai:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.time_zone = timezone(offset=timedelta(hours=UtcOffset))
        self.client = genai.Client(api_key=f"{env.gemini_api_key}")

        self.histories: dict[int, list[types.Content]] = {}
    
    async def send(self, message):
        try:
            guild_id = message.guild.id

            chat = self.client.chats.create(
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
                ),
                history=self.get_history(guild_id)
            )
            
            message_no_prefix = list(str(message.content).split(" "))[1:]
            message_no_prefix = " ".join(message_no_prefix)
            message_str = f"time:{datetime.now(tz=self.time_zone).strftime('%Y-%m-%d %H:%M')} author:{message.author} message:{message_no_prefix}"

            response = chat.send_message(message_str)

            response_json = json.loads(response.text)
            response_text = response_json["text"]

            self.append_history(guild_id, message_str, response_text)

            if "cmd" in response_json:
                response_cmd = response_json["cmd"]
                if type(response_cmd) is list:
                    self.solve_cmd(response_cmd, message.channel.id)

            await message.channel.send(response_text)
        except APIError as e:
            if e.code == 429:
                await message.channel.send("我累了，有什麼話等下再說。")
            else:
                print("unknow API err", file=stderr)
                print(e, file=stderr)
                await message.channel.send("你說什麼？我剛剛沒聽清楚。")
            return
        except json.JSONDecodeError as e:
            print(f"json err\nresponse text:\n{response.text}", file=stderr)
            return
        except Exception as e:
            print(f"unknow err: {e}", file=stderr)
            print(f"message: {message_str}", file=stderr)
            return
    
    def solve_cmd(self, cmd: list[dict], channel_id):
        for action in cmd:
            new_mai_clock(
                int(action["id"]),
                action["time"],
                action["date"],
                action["content"],
                channel_id,
                self.clock_func
            )
    
    async def clock_func(self, clock):
        channel = self.bot.get_channel(clock.channel_id)
        try:
            await channel.send(f"{clock.content}")
        except Exception as e:
            print(f"err while trig clock: {e}")
            print(f"clock data: {clock.get_clock_data}")
            return
        self.append_history(channel.guild.id, "", f"{clock.content}")

    def check_history_legal(self, guild_id):
        if guild_id not in self.histories.keys():
            raise f"illegal chat history: {guild_id}"

        for i in range(self.histories[guild_id]):
            if i % 2:
                if self.histories[guild_id][i].role != "model":
                    raise f"illegal chat history: {guild_id}"
            else:
                if self.histories[guild_id][i].role != "user":
                    raise f"illegal chat history: {guild_id}"
                
    def get_history(self, guild_id):
        if guild_id not in self.histories.keys():
            self.histories[guild_id] = []

        if len(self.histories[guild_id]) > MaxChatHistoryAmount * 2:
            self.histories[guild_id] = self.histories[guild_id][:-MaxChatHistoryAmount * 2]
        
        return self.histories[guild_id]
    
    def append_history(self, guild_id, user_text, model_text):
        if guild_id not in self.histories.keys():
            self.histories[guild_id] = []
        
        user_msg = types.Content(
            role="user",
            parts=[types.Part(text=user_text)]
        )
        model_msg = types.Content(
            role="model", 
            parts=[types.Part(text=model_text)]
        )

        self.histories[guild_id].extend([user_msg, model_msg])

        if len(self.histories[guild_id]) > MaxChatHistoryAmount * 2:
            self.histories[guild_id] = self.histories[guild_id][:-MaxChatHistoryAmount * 2]
