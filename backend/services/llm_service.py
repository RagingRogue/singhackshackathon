from groq import Groq
from core.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def ask_llm(messages):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.8,
        max_completion_tokens=1024,
    )
    return completion.choices[0].message.content.strip()
