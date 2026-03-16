import os
import requests
from urllib.parse import quote

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse

app = FastAPI()

# ENV VARIABLES (set trên Railway)
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
APP_BASE_URL = os.getenv("APP_BASE_URL", "").rstrip("/")


# -------------------------
# HOME PAGE
# -------------------------
@app.get("/")
def home():

    html = """
    <html>
    <head>
        <title>TikTok Integration Demo</title>
        <style>
            body{
                font-family: Arial;
                text-align:center;
                margin-top:120px;
            }
            button{
                padding:14px 28px;
                font-size:18px;
                background:#000;
                color:white;
                border:none;
                border-radius:6px;
                cursor:pointer;
            }
        </style>
    </head>
    <body>

        <h1>TikTok Integration Demo</h1>

        <p>This demo shows TikTok Login Kit integration.</p>

        <br>

        <a href="/login">
            <button>Login with TikTok</button>
        </a>

    </body>
    </html>
    """

    return HTMLResponse(html)


# -------------------------
# LOGIN REDIRECT
# -------------------------
@app.get("/login")
def login():

    redirect_uri = f"{APP_BASE_URL}/callback"

    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        "&response_type=code"
        "&scope=user.info.basic"
        f"&redirect_uri={quote(redirect_uri, safe='')}"
    )

    return RedirectResponse(auth_url)


# -------------------------
# CALLBACK
# -------------------------
@app.get("/callback")
def callback(code: str = "", error: str = ""):

    if error:
        return HTMLResponse(
            f"""
            <h2>Login failed</h2>
            <p>Error: {error}</p>
            <a href="/">Back</a>
            """,
            status_code=400
        )

    redirect_uri = f"{APP_BASE_URL}/callback"

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    response = requests.post(
        token_url,
        headers=headers,
        data=data,
        timeout=30
    )

    result = response.json()

    if "access_token" not in result:

        return HTMLResponse(
            f"""
            <h2>Token exchange failed</h2>
            <pre>{result}</pre>
            <a href="/">Back</a>
            """,
            status_code=400
        )

    access_token = result["access_token"]
    open_id = result["open_id"]

    html = f"""
    <html>
    <head>
        <title>TikTok Login Success</title>
        <style>
            body{{
                font-family: Arial;
                text-align:center;
                margin-top:120px;
            }}
            pre{{
                background:#eee;
                padding:10px;
            }}
        </style>
    </head>

    <body>

        <h1>TikTok login success</h1>

        <p>User authenticated successfully.</p>

        <h3>Open ID</h3>
        <pre>{open_id}</pre>

        <h3>Access Token</h3>
        <pre>{access_token[:40]}...</pre>

        <br>

        <a href="/">Back to home</a>

    </body>
    </html>
    """

    return HTMLResponse(html)
