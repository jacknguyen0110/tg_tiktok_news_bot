import os
from fastapi import FastAPI
import requests

from app.news import get_hot_news
from app.ai_writer import generate_script
from app.tts import generate_voice
from app.video import render_video
from app.sheets_logger import log_content

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_ALLOWED_CHAT_ID")

app = FastAPI()

def send_video(path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    files = {"video": open(path,"rb")}
    requests.post(url, data={"chat_id":CHAT_ID}, files=files)

@app.get("/")
def home():
    return {"status":"running"}

@app.post("/hotnews")
async def hotnews():

    news = get_hot_news()

    script = generate_script(news)

    audio = generate_voice(script)

    video = render_video(script, audio)

    send_video(video)

    log_content(news, script)

    return {"status":"video_created"}