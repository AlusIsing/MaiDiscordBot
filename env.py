import os

bot_key = os.getenv("DISCORD_BOT_KEY")
master_discord_id = os.getenv("MASTER_DISCORD_ID")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if __name__ == "__main__":
    print(f"discord bot key: {bot_key}")
    print(f"master discord ID: {master_discord_id}")
    print(f"Gemini API key: {gemini_api_key}")
