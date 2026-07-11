from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

print("API:", os.getenv("GOOGLE_API_KEY")[:15], "...")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

try:
    response = llm.invoke("Say hello")
    print(response.content)
except Exception as e:
    print(type(e).__name__)
    print(e)