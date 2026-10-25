# -*- coding: utf-8 -*-
import http.server
import json
import os
import random
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
DATA_FILE = "frost_pro_db.json"

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
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frost Pro - Secure Messenger</title>
    <style>
        * { box-sizing: border-box; }
        body { background: #0b141a; color: #e9edef; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100dvh; overflow: hidden; }
        .header { background: #202c33; padding: 10px 15px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2a3942; flex-shrink: 0; }
        .logo-area { display: flex; align-items: center; gap: 8px; font-weight: bold; font-size: 1.1rem; color: #38bdf8; }
        .container { flex: 1; display: flex; flex-direction: column; max-width: 600px; width: 100%; margin: 0 auto; background: #0b141a; overflow: hidden; height: 100%; }
        #auth-screen { padding: 30px 20px; text-align: center; margin: auto; background: #111b21; border-radius: 12px; width: 90%; max-width: 380px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        input[type="text"], button { width: 100%; padding: 12px; margin-top: 12px; background: #2a3942; color: #fff; border: none; border-radius: 8px; font-size: 0.95rem; }
        button { background: #38bdf8; color: #0f172a; font-weight: bold; cursor: pointer; }
        button:hover { background: #0ea5e9; }
        .chat-container { display: none; flex-direction: column; height: 100%; width: 100%; overflow: hidden; }
        .chat-messages { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; background-image: radial-gradient(#111b21 1px, transparent 1px); background-size: 20px 20px; }
        .msg { max-width: 75%; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; word-break: break-all; position: relative; box-shadow: 0 1px 0.5px rgba(0,0,0,0.3); }
        .msg.sent { background: #0369a1; align-self: flex-end; border-top-right-radius: 0; }
        .msg.received { background: #202c33; align-self: flex-start; border-top-left-radius: 0; }
        .msg img { max-width: 100%; border-radius: 6px; margin-top: 5px; }
        .msg-meta { font-size: 0.7rem; color: #bae6fd; text-align: right; margin-top: 4px; display: flex; align-items: center; justify-content: flex-end; gap: 3px; }
        .chat-input-bar { background: #202c33; padding: 10px 15px; display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
        .chat-input-bar input[type="text"] { margin: 0; flex: 1; background: #2a3942; }
        .icon-btn { background: transparent; width: auto; padding: 8px; font-size: 1.2rem; cursor: pointer; margin: 0; color: #8696a0; border: none; }
        .profile-badge { display: flex; align-items: center; gap: 10px; font-size: 0.85rem; background: #111b21; padding: 8px 12px; border-radius: 8px; margin: 8px; flex-shrink: 0; }
        .avatar { width: 35px; height: 35px; border-radius: 50%; object-fit: cover; background: #374151; display: flex; align-items: center; justify-content: center; font-weight: bold; overflow:hidden; flex-shrink: 0; }
        .avatar img { width:100%; height:100%; object-fit:cover; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-area">
            <span>❄️</span> Frost Pro
        </div>
    </div>
    <div class="container">
        <div id="auth-screen">
            <h2>Frost Pro</h2>
            <p style="color: #8696a0; font-size: 0.85rem;">Secure Encrypted Messenger</p>
            <input type="text" id="usernameInput" placeholder="Enter your username">
            <button onclick="registerUser()">Connect & Generate Number</button>
        </div>
        <div class="chat-container" id="chatScreen">
            <div class="profile-badge" id="profileBadge">
                <div class="avatar" id="userAvatarBox">U</div>
                <div style="flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                    <strong id="profileName"></strong><br>
                    <span style="color: #38bdf8; font-size: 0.75rem;" id="profileNumber"></span>
                </div>
                <label style="cursor:pointer; font-size: 0.75rem; background: #2a3942; padding: 6px 10px; border-radius: 6px; white-space:nowrap;">
                    Edit Avatar <input type="file" accept="image/*" style="display:none;" onchange="updateAvatar(this)">
                </label>
            </div>
            <div class="chat-messages" id="chatStream"></div>
            <div id="previewContainer" style="padding: 4px 15px; font-size: 0.75rem; color: #38bdf8; background:#111b21; display:none;">Image Attached ✓</div>
            <div class="chat-input-bar">
                <label class="icon-btn" title="Send Image">
                    📷 <input type="file" id="imageInput" accept="image/*" style="display:none;" onchange="previewMedia(this)">
                </label>
                <input type="text" id="msgText" placeholder="Type a message..." onkeypress="if(event.key === 'Enter') { sendMessage(); return false; }">
                <button class="icon-btn" onclick="sendMessage()" style="background:#38bdf8; color:#0f172a; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">➤</button>
            </div>
        </div>
    </div>
    <script>
        let currentUser = "";
        let currentNumber = "";
        let selectedImageBase64 = "";

        function registerUser() {
            let u = document.getElementById('usernameInput').value.trim();
            if(!u) return alert("Enter a username!");
            fetch('/api/connect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u})
            }).then(res => res.json()).then(data => {
                currentUser = u;
                currentNumber = data.virtual_number;
                document.getElementById('auth-screen').style.display = 'none';
                document.getElementById('chatScreen').style.display = 'flex';
                document.getElementById('profileName').innerText = u;
                document.getElementById('profileNumber').innerText = "Virtual # : " + currentNumber;
                if(data.profile_pic) {
                    document.getElementById('userAvatarBox').innerHTML = '<img src="'+data.profile_pic+'">';
                } else {
                    document.getElementById('userAvatarBox').innerText = u.charAt(0).toUpperCase();
                }
                loadChats();
                setInterval(loadChats, 3000);
            });
        }

        function previewMedia(input) {
            if(input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = function(e) {
                    selectedImageBase64 = e.target.result;
                    document.getElementById('previewContainer').style.display = 'block';
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        function updateAvatar(input) {
            if(input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = function(e) {
                    fetch('/api/profile_pic', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({username: currentUser, image: e.target.result})
                    }).then(() => {
                        document.getElementById('userAvatarBox').innerHTML = '<img src="'+e.target.result+'">';
                        alert("Profile picture updated!");
                    });
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        function sendMessage() {
            let textInput = document.getElementById('msgText');
            let text = textInput.value.trim();
            if(!text && !selectedImageBase64) return;
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: currentUser, text: text, image: selectedImageBase64})
            }).then(() => {
                textInput.value = "";
                selectedImageBase64 = "";
                document.getElementById('previewContainer').style.display = 'none';
                document.getElementById('imageInput').value = "";
                loadChats();
            });
        }

        function loadChats() {
            if(!currentUser) return;
            fetch('/api/chats').then(res => res.json()).then(data => {
                let box = document.getElementById('chatStream');
                box.innerHTML = data.map(m => {
                    let isMe = m.username === currentUser;
                    let timeStr = "";
                    try {
                        timeStr = m.time.split(' ')[1].substring(0,5);
                    } catch(e) {
                        timeStr = "12:00";
                    }
                    return `
                        <div class="msg ${isMe ? 'sent' : 'received'}">
                            ${!isMe ? '<strong style="color: #38bdf8; font-size: 0.8rem; display:block; margin-bottom: 2px;">'+m.username+'</strong>' : ''}
                            ${m.text ? '<div>'+m.text+'</div>' : ''}
                            ${m.image ? '<img src="'+m.image+'">' : ''}
                            <div class="msg-meta">
                                <span>'+timeStr+'</span>
                                ${isMe ? '<span style="color: #38bdf8; font-weight: bold;">✓✓</span>' : ''}
                            </div>
                        </div>
                    `;
                }).join('');
                box.scrollTop = box.scrollHeight;
            });
        }
    </script>
</body>
</html>
"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path == '/api/chats':
            db = load_db()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(db["chats"]).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode('utf-8')) if body else {}
        db = load_db()

        if self.path == '/api/connect':
            u = data.get("username")
            if u not in db["users"]:
                db["users"][u] = {
                    "virtual_number": f"+1 ({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
                    "profile_pic": ""
                }
                save_db(db)
            res_data = db["users"][u]
            res_data["username"] = u
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res_data).encode('utf-8'))

        elif self.path == '/api/profile_pic':
            u = data.get("username")
            img = data.get("image")
            if u in db["users"]:
                db["users"][u]["profile_pic"] = img
                save_db(db)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        elif self.path == '/api/chat':
            db["chats"].append({
                "username": data.get("username"),
                "text": data.get("text", ""),
                "image": data.get("image", ""),
                "time": str(datetime.now())
            })
            save_db(db)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

if __name__ == '__main__':
    print(f"❄️ Frost Pro running on port {PORT}")
    http.server.HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
