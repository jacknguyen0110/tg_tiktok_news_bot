import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_script(news):

    prompt = f'''
Viết script video TikTok tiếng Việt 45 giây.

Tin:
{news}

Format:
Hook:
Script:
Caption:
Hashtags:
'''

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )

    return response.choices[0].message.content