import os

from google import genai

# init Client
client = genai.Client(api_key=f"{os.getenv('GEMINI_API_KEY')}")

try:
    # output content one time
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents="hello, please return 'api test success'"
    )
    print(f"API return: {response.text}")
    
    # check token usage
    print(f"token usage: {response.usage_metadata.total_token_count}")

except Exception as e:
    print(f"err: {e}")