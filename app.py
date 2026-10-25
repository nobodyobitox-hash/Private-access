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
        .header { background: #202c33; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2a3942; flex-shrink: 0; }
        .logo-area { display: flex; align-items: center; gap: 8px; font-weight: bold; font-size: 1.1rem; color: #38bdf8; }
        .container { flex: 1; display: flex; flex-direction: column; max-width: 600px; width: 100%; margin: 0 auto; background: #0b141a; overflow: hidden; height: 100%; }
        #auth-screen { padding: 30px 20px; text-align: center; margin: auto; background: #111b21; border-radius: 12px; width: 90%; max-width: 380px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        input[type="text"], button { width: 100%; padding: 12px; margin-top: 12px; background: #2a3942; color: #fff; border: none; border-radius: 8px; font-size: 0.95rem; }
        button { background: #38bdf8; color: #0f172a; font-weight: bold; cursor: pointer; }
        button:hover { background: #0ea5e9; }
        
        .app-layout { display: none; flex-direction: column; height: 100%; width: 100%; overflow: hidden; }
        .content-section { flex: 1; display: none; flex-direction: column; overflow: hidden; }
        .content-section.active { display: flex; }
        
        .nav-bar { background: #202c33; display: flex; border-top: 1px solid #2a3942; flex-shrink: 0; }
        .nav-item { flex: 1; padding: 12px; text-align: center; color: #8696a0; font-size: 0.8rem; cursor: pointer; font-weight: bold; background: none; border: none; margin: 0; border-radius: 0; }
        .nav-item.active { color: #38bdf8; border-top: 2px solid #38bdf8; background: #111b21; }

        .chat-messages { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; background-image: radial-gradient(#111b21 1px, transparent 1px); background-size: 20px 20px; }
        .msg { max-width: 75%; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; word-break: break-all; position: relative; box-shadow: 0 1px 0.5px rgba(0,0,0,0.3); }
        .msg.sent { background: #0369a1; align-self: flex-end; border-top-right-radius: 0; }
        .msg.received { background: #202c33; align-self: flex-start; border-top-left-radius: 0; }
        .msg img { max-width: 100%; border-radius: 6px; margin-top: 5px; }
        .msg-meta { font-size: 0.7rem; color: #bae6fd; text-align: right; margin-top: 4px; display: flex; align-items: center; justify-content: flex-end; gap: 3px; }
        .chat-input-bar { background: #202c33; padding: 10px 15px; display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
        .chat-input-bar input[type="text"] { margin: 0; flex: 1; background: #2a3942; }
        .icon-btn { background: transparent; width: auto; padding: 8px; font-size: 1.2rem; cursor: pointer; margin: 0; color: #8696a0; border: none; }

        .active-chats-list { padding: 15px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 10px; }
        .user-card { background: #111b21; padding: 12px 15px; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; border-left: 4px solid #38bdf8; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .user-info { display: flex; align-items: center; gap: 12px; }
        .mini-avatar { width: 40px; height: 40px; border-radius: 50%; background: #374151; display: flex; align-items: center; justify-content: center; font-weight: bold; overflow: hidden; }
        .mini-avatar img { width: 100%; height: 100%; object-fit: cover; }

        .settings-box { padding: 20px; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; flex: 1; }
        .profile-card { background: #111b21; padding: 20px; border-radius: 12px; display: flex; align-items: center; gap: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }
        .avatar { width: 55px; height: 55px; border-radius: 50%; object-fit: cover; background: #374151; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; overflow:hidden; flex-shrink: 0; }
        .avatar img { width:100%; height:100%; object-fit:cover; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-area">
            <span>❄️</span> <span id="headerTitle">Frost Pro</span>
        </div>
    </div>
    <div class="container">
        <!-- Auth Screen -->
        <div id="auth-screen">
            <h2>Frost Pro</h2>
            <p style="color: #8696a0; font-size: 0.85rem;">Secure Encrypted Messenger</p>
            <input type="text" id="usernameInput" placeholder="Enter your username">
            <button onclick="registerUser()">Connect & Generate Number</button>
        </div>

        <!-- Main App Layout -->
        <div class="app-layout" id="appLayout">
            <!-- Section 1: Chat Room View -->
            <div class="content-section active" id="sec-chats">
                <div style="background: #111b21; padding: 8px 15px; font-size: 0.8rem; color: #38bdf8; border-bottom: 1px solid #2a3942; display: flex; justify-content: space-between; align-items: center;">
                    <span id="activeChatTitle">🌐 General Room (300+ Users)</span>
                    <button onclick="switchTab('active')" style="width: auto; padding: 3px 8px; margin: 0; font-size: 0.75rem; background: #2a3942; color: #e9edef;">Change Chat</button>
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

            <!-- Section 2: 1-to-1 DMs & Number Lookup -->
            <div class="content-section" id="sec-active">
                <div class="active-chats-list">
                    <h3 style="color: #38bdf8; margin-top:0;">1-to-1 Private Messenger</h3>
                    <p style="color: #8696a0; font-size: 0.85rem;">Enter a user's virtual number or tap an online user below:</p>
                    
                    <!-- Number Lookup Box -->
                    <div style="background: #111b21; padding: 12px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #2a3942;">
                        <label style="font-size: 0.75rem; color: #38bdf8; font-weight: bold;">LOOKUP BY VIRTUAL NUMBER</label>
                        <input type="text" id="targetNumberInput" placeholder="e.g. +1 (334) 642-5856" style="margin-top:6px; background:#2a3942;">
                        <button onclick="startChatByNumber()" style="margin-top:8px;">Open 1-to-1 Chat</button>
                    </div>

                    <div class="user-card" onclick="openChatWith('general', '🌐 General Room (300+ Users)')">
                        <div class="user-info">
                            <div class="mini-avatar" style="background:#0369a1;">🌐</div>
                            <div>
                                <strong>General Room (300+ Users)</strong><br>
                                <span style="font-size:0.75rem; color:#8696a0;">Public community lobby</span>
                            </div>
                        </div>
                        <button style="width:auto; padding:5px 10px; margin:0; font-size:0.75rem;">Open</button>
                    </div>
                    <div id="usersListContainer"></div>
                </div>
            </div>

            <!-- Section 3: Settings -->
            <div class="content-section" id="sec-settings">
                <div class="settings-box">
                    <h3 style="color: #38bdf8; margin-top:0;">Profile & Settings</h3>
                    <div class="profile-card">
                        <div class="avatar" id="userAvatarBox">U</div>
                        <div style="flex:1; overflow:hidden;">
                            <strong id="profileName" style="font-size: 1.05rem;"></strong><br>
                            <span style="color: #38bdf8; font-size: 0.8rem;" id="profileNumber"></span>
                        </div>
                    </div>
                    <div style="background: #111b21; padding: 15px; border-radius: 12px;">
                        <p style="margin: 0 0 10px 0; font-size: 0.85rem; color: #8696a0;">Change Profile Picture</p>
                        <label style="cursor:pointer; display:block; text-align:center; font-size: 0.85rem; background: #2a3942; padding: 10px; border-radius: 8px; color: #38bdf8; font-weight: bold;">
                            Upload New Avatar <input type="file" accept="image/*" style="display:none;" onchange="updateAvatar(this)">
                        </label>
                    </div>
                </div>
            </div>

            <!-- Bottom Navigation Bar -->
            <div class="nav-bar">
                <button class="nav-item active" id="nav-chats" onclick="switchTab('chats')">💬 Chat Room</button>
                <button class="nav-item" id="nav-active" onclick="switchTab('active')">👤 1-to-1 DMs</button>
                <button class="nav-item" id="nav-settings" onclick="switchTab('settings')">⚙️ Settings</button>
            </div>
        </div>
    </div>
    <script>
        let currentUser = "";
        let currentNumber = "";
        let currentRecipient = "general";
        let selectedImageBase64 = "";
        let globalUsersCache = {};

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
                document.getElementById('appLayout').style.display = 'flex';
                document.getElementById('profileName').innerText = u;
                document.getElementById('profileNumber').innerText = "Virtual # : " + currentNumber;
                if(data.profile_pic) {
                    document.getElementById('userAvatarBox').innerHTML = '<img src="'+data.profile_pic+'">';
                } else {
                    document.getElementById('userAvatarBox').innerText = u.charAt(0).toUpperCase();
                }
                loadAppData();
                setInterval(loadAppData, 3000);
            });
        }

        function switchTab(tabName) {
            document.querySelectorAll('.content-section').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            
            if(tabName === 'chats') {
                document.getElementById('sec-chats').classList.add('active');
                document.getElementById('nav-chats').classList.add('active');
            } else if(tabName === 'active') {
                document.getElementById('sec-active').classList.add('active');
                document.getElementById('nav-active').classList.add('active');
                loadUsersList();
            } else if(tabName === 'settings') {
                document.getElementById('sec-settings').classList.add('active');
                document.getElementById('nav-settings').classList.add('active');
            }
        }

        function openChatWith(recipientName, displayName) {
            currentRecipient = recipientName;
            document.getElementById('activeChatTitle').innerText = displayName;
            switchTab('chats');
            loadChats();
        }

        function startChatByNumber() {
            let targetNum = document.getElementById('targetNumberInput').value.trim();
            if(!targetNum) return alert("Please enter a virtual number!");
            
            let foundUsername = "";
            for(let uname in globalUsersCache) {
                if(globalUsersCache[uname].virtual_number.trim() === targetNum) {
                    foundUsername = uname;
                    break;
                }
            }

            if(!foundUsername) {
                return alert("No registered user found with number: " + targetNum);
            }

            if(foundUsername === currentUser) {
                return alert("You cannot chat with yourself!");
            }

            openChatWith(foundUsername, "💬 Private Chat: " + foundUsername + " (" + targetNum + ")");
            document.getElementById('targetNumberInput').value = "";
        }

        function loadAppData() {
            loadChats();
            if(document.getElementById('sec-active').classList.contains('active')) {
                loadUsersList();
            }
        }

        function loadUsersList() {
            fetch('/api/users').then(res => res.json()).then(users => {
                globalUsersCache = users;
                let listContainer = document.getElementById('usersListContainer');
                let html = "";
                for(let uname in users) {
                    if(uname === currentUser) continue;
                    let uData = users[uname];
                    let avatarHtml = uData.profile_pic ? '<img src="'+uData.profile_pic+'">' : uname.charAt(0).toUpperCase();
                    html += `
                        <div class="user-card" onclick="openChatWith('${uname}', '💬 Private Chat: ${uname} (${uData.virtual_number})')">
                            <div class="user-info">
                                <div class="mini-avatar">${avatarHtml}</div>
                                <div>
                                    <strong>${uname}</strong><br>
                                    <span style="font-size:0.75rem; color:#38bdf8;">${uData.virtual_number}</span>
                                </div>
                            </div>
                            <button style="width:auto; padding:5px 10px; margin:0; font-size:0.75rem;">Chat 1-to-1</button>
                        </div>
                    `;
                }
                listContainer.innerHTML = html;
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
                body: JSON.stringify({
                    username: currentUser,
                    recipient: currentRecipient,
                    text: text,
                    image: selectedImageBase64
                })
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
                let filtered = data.filter(m => {
                    if(currentRecipient === 'general') {
                        return !m.recipient || m.recipient === 'general' || m.recipient === 'global';
                    } else {
                        return (m.username === currentUser && m.recipient === currentRecipient) ||
                               (m.username === currentRecipient && m.recipient === currentUser);
                    }
                });

                box.innerHTML = filtered.map(m => {
                    let isMe = m.username === currentUser;
                    let timeStr = "12:00";
                    try {
                        timeStr = m.time.split(' ')[1].substring(0,5);
                    } catch(e) {}
                    return `
                        <div class="msg ${isMe ? 'sent' : 'received'}">
                            ${!isMe ? '<strong style="color: #38bdf8; font-size: 0.8rem; display:block; margin-bottom: 2px;">'+m.username+'</strong>' : ''}
                            ${m.text ? '<div>'+m.text+'</div>' : ''}
                            ${m.image ? '<img src="'+m.image+'">' : ''}
                            <div class="msg-meta">
                                <span>` + timeStr + `</span>
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
        elif self.path == '/api/users':
            db = load_db()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(db["users"]).encode('utf-8'))
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
                "recipient": data.get("recipient", "general"),
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
