import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.news import get_hot_news
from app.ai_writer import generate_script
from app.tts import generate_voice
from app.sheets_logger import log_content

app = FastAPI()
templates = Jinja2Templates(directory="templates")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_ALLOWED_CHAT_ID", "")
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
APP_BASE_URL = os.getenv("APP_BASE_URL", "").rstrip("/")


def get_redirect_uri() -> str:
    return f"{APP_BASE_URL}/callback"


def send_telegram_message(text: str) -> None:
    if not TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text,
        },
        timeout=30,
    )


def send_telegram_video(path: str, caption: str = "") -> None:
    if not TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    with open(path, "rb") as f:
        files = {"video": f}
        data = {"chat_id": CHAT_ID}
        if caption:
            data["caption"] = caption
        requests.post(url, data=data, files=files, timeout=120)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": "GlobalNewsBot",
            "app_base_url": APP_BASE_URL,
        },
    )


@app.get("/health")
def health():
    return {"status": "running"}


@app.get("/login")
def login():
    if not CLIENT_KEY:
        return JSONResponse(
            status_code=500,
            content={"error": "Missing TIKTOK_CLIENT_KEY"},
        )

    if not APP_BASE_URL:
        return JSONResponse(
            status_code=500,
            content={"error": "Missing APP_BASE_URL"},
        )

    redirect_uri = get_redirect_uri()

    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        "&response_type=code"
        "&scope=user.info.profile,video.publish"
        f"&redirect_uri={redirect_uri}"
    )

    return RedirectResponse(auth_url)


@app.get("/callback", response_class=HTMLResponse)
def callback(code: str = "", error: str = ""):
    if error:
        return HTMLResponse(
            f"""
            <html>
              <body style="font-family:Arial;text-align:center;padding-top:80px">
                <h2>TikTok login failed</h2>
                <p>{error}</p>
                <a href="/">Back</a>
              </body>
            </html>
            """,
            status_code=400,
        )

    return HTMLResponse(
        f"""
        <html>
          <body style="font-family:Arial;text-align:center;padding-top:80px">
            <h2>TikTok login success</h2>
            <p>Authorization code received.</p>
            <p style="word-break:break-all;max-width:900px;margin:0 auto">{code}</p>
            <br>
            <a href="/">Back to home</a>
          </body>
        </html>
        """
    )


@app.get("/generate")
def generate_demo():
    return {
        "message": "Demo generate completed",
        "note": "This endpoint is for TikTok review demo flow.",
    }


@app.post("/hotnews")
async def hotnews():
    """
    Flow thật:
    1. Lấy tin nóng
    2. Viết script
    3. Tạo audio
    4. Render video
    5. Gửi Telegram
    6. Ghi Google Sheet
    """

    try:
        news = get_hot_news()
        script = generate_script(news)
        audio = generate_voice(script)

        # Lazy import để app vẫn boot được kể cả moviepy/ffmpeg có vấn đề
        from app.video import render_video

        video = render_video(script, audio)

        send_telegram_video(video, caption="Hot news video generated")
        log_content(news, script)

        return {
            "status": "success",
            "news_title": news.get("title", ""),
            "script_preview": script[:200],
        }

    except Exception as e:
        send_telegram_message(f"Hotnews error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )
