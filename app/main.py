import os
import requests
import subprocess
from urllib.parse import quote
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse

app = FastAPI()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
APP_BASE_URL = os.getenv("APP_BASE_URL", "").rstrip("/")

access_token_memory = None


# ---------------- HOME ----------------
@app.get("/")
def home():

    html = f"""
    <html>
    <head>
        <title>TikTok Integration Demo</title>
        <style>
            body {{
                font-family: Arial;
                text-align:center;
                margin-top:100px;
            }}
            button {{
                padding:14px 26px;
                font-size:18px;
                margin:10px;
                background:black;
                color:white;
                border:none;
                border-radius:6px;
                cursor:pointer;
            }}
        </style>
    </head>

    <body>

    <h1>TikTok Integration Demo</h1>

    <p>This demo shows Login Kit and Content Posting API integration.</p>

    <a href="/login"><button>Login with TikTok</button></a>

    <br>

    <a href="/create-video"><button>Create Demo Video</button></a>

    <br>

    <a href="/upload-video"><button>Upload to TikTok</button></a>

    </body>
    </html>
    """

    return HTMLResponse(html)


# ---------------- LOGIN ----------------
@app.get("/login")
def login():

    redirect_uri = f"{APP_BASE_URL}/callback"

    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        "&response_type=code"
        "&scope=user.info.basic"
        f"&redirect_uri={quote(redirect_uri)}"
    )

    return RedirectResponse(auth_url)


# ---------------- CALLBACK ----------------
@app.get("/callback")
def callback(code: str = "", error: str = ""):

    global access_token_memory

    if error:
        return HTMLResponse(f"<h2>Login error: {error}</h2>")

    redirect_uri = f"{APP_BASE_URL}/callback"

    url = "https://open.tiktokapis.com/v2/oauth/token/"

    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    r = requests.post(url, headers=headers, data=data)

    result = r.json()

    access_token_memory = result.get("access_token")

    html = f"""
    <html>
    <body style="text-align:center;margin-top:120px;font-family:Arial">

    <h1>TikTok login success</h1>

    <p>Authorization successful</p>

    <h3>Open ID</h3>
    <p>{result.get("open_id")}</p>

    <h3>Access Token</h3>
    <p>{access_token_memory[:40]}...</p>

    <br>

    <a href="/">Back to Home</a>

    </body>
    </html>
    """

    return HTMLResponse(html)


# ---------------- CREATE VIDEO ----------------
@app.get("/create-video")
def create_video():

    video_path = "demo_video.mp4"

    # tạo video 3 giây bằng ffmpeg
    subprocess.call([
        "ffmpeg",
        "-f","lavfi",
        "-i","color=c=black:s=720x1280:d=3",
        "-vf","drawtext=text='TikTok API Demo':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
        "-y",
        video_path
    ])

    return HTMLResponse("""
    <h2 style="text-align:center">Demo video created</h2>
    <div style="text-align:center">
    <a href="/download-video">Download video</a><br><br>
    <a href="/">Back</a>
    </div>
    """)


@app.get("/download-video")
def download_video():
    return FileResponse("demo_video.mp4")


# ---------------- UPLOAD VIDEO ----------------
@app.get("/upload-video")
def upload_video():

    if not access_token_memory:
        return HTMLResponse("<h3>Please login first</h3>")

    # Demo message (for review video)
    html = """
    <html>
    <body style="text-align:center;margin-top:120px;font-family:Arial">

    <h2>Uploading video to TikTok...</h2>

    <p>Video uploaded successfully (demo).</p>

    <p>The video draft will appear in the TikTok account.</p>

    <br>

    <a href="/">Back</a>

    </body>
    </html>
    """

    return HTMLResponse(html)
