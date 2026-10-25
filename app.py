import http.server
import json
import os
import random
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
DATA_FILE = "frost_db.json"

def load_db():
    if not os.path.exists(DATA_FILE):
        db = {"users": {}, "chats": []}
        with open(DATA_FILE, "w") as f:
            json.dump(db, f)
        return db
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}, "chats": []}

def save_db(db):
    with open(DATA_FILE, "w") as f:
        json.dump(db, f, indent=4)

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frost - Secure Messenger</title>
    <style>
        body { background: #0b141a; color: #e9edef; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        .header { background: #202c33; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2a3942; }
        .logo-area { display: flex; align-items: center; gap: 10px; font-weight: bold; font-size: 1.2rem; color: #38bdf8; }
        .container { flex: 1; display: flex; flex-direction: column; max-width: 600px; width: 100%; margin: 0 auto; background: #0b141a; overflow: hidden; }
        #auth-screen { padding: 40px 20px; text-align: center; margin: auto; background: #111b21; border-radius: 12px; width: 90%; max-width: 380px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        input, button { width: 100%; padding: 12px; margin-top: 12px; background: #2a3942; color: #fff; border: none; border-radius: 8px; box-sizing: border-box; font-size: 0.95rem; }
        button { background: #38bdf8; color: #0f172a; font-weight: bold; cursor: pointer; }
        button:hover { background: #0ea5e9; }
        .chat-container { display: none; flex-direction: column; height: 100%; width: 100%; }
        .chat-messages { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; background-image: radial-gradient(#111b21 1px, transparent 1px); background-size: 20px 20px; }
        .msg { max-width: 75%; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; word-break: break-all; position: relative; box-shadow: 0 1px 0.5px rgba(0,0,0,0.3); }
        .msg.sent { background: #0369a1; align-self: flex-end; border-top-right-radius: 0; }
        .msg.received { background: #202c33; align-self: flex-start; border-top-left-radius: 0; }
        .msg img { max-width: 100%; border-radius: 6px; margin-top: 5px; }
        .msg-meta { font-size: 0.7rem; color: #bae6fd; text-align: right; margin-top: 4px; display: flex; align-items: center; justify-content: flex-end; gap: 3px; }
        .chat-input-bar { background: #202c33; padding: 10px 15px; display: flex; align-items: center; gap: 10px; }
        .chat-input-bar input[type="text"] { margin: 0; flex: 1; background: #2a3942; }
        .icon-btn { background: transparent; width:

