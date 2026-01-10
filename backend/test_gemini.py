import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="Say hello and confirm you are working"
)

print(response.text)
