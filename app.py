# -*- coding: utf-8 -*-
import http.server, json, os, random
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
DB_FILE = "frost_pro_db.json"

def db_load():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"users": {}, "chats": []}, f)
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"users": {}, "chats": []}

def db_save(d):
    with open(DB_FILE, "w") as f:
        json.dump(d, f, indent=4)

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Frost Pro</title>
    <style>
        * { box-sizing: border-box; }
        body { background: #0b141a; color: #e9edef; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100dvh; overflow: hidden; }
        .header { background: #202c33; padding: 12px 20px; font-weight: bold; color: #38bdf8; font-size: 1.1rem; }
        .container { flex: 1; display: flex; flex-direction: column; max-width: 600px; width: 100%; margin: 0 auto; overflow: hidden; }
        #auth { padding: 40px 20px; text-align: center; margin: auto; background: #111b21; border-radius: 12px; width: 90%; max-width: 380px; }
        input, button { width: 100%; padding: 12px; margin-top: 12px; background: #2a3942; color: #fff; border: none; border-radius: 8px; font-size: 0.95rem; }
        button { background: #38bdf8; color: #0f172a; font-weight: bold; cursor: pointer; }
        .app { display: none; flex-direction: column; height: 100%; overflow: hidden; }
        .tab-content { flex: 1; display: none; flex-direction: column; overflow: hidden; }
        .tab-content.active { display: flex; }
        .nav { background: #202c33; display: flex; border-top: 1px solid #2a3942; flex-shrink: 0; }
        .nav-btn { flex: 1; padding: 12px; text-align: center; color: #8696a0; background: none; border: none; font-weight: bold; font-size: 0.8rem; cursor: pointer; }
        .nav-btn.active { color: #38bdf8; background: #111b21; border-top: 2px solid #38bdf8; }
        .messages { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; background: #0b141a; }
        .msg { max-width: 75%; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; word-break: break-all; }
        .msg.sent { background: #0369a1; align-self: flex-end; }
        .msg.received { background: #202c33; align-self: flex-start; }
        .msg img { max-width: 100%; border-radius: 6px; margin-top: 5px; }
        .input-bar { background: #202c33; padding: 10px 15px; display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
        .input-bar input { margin: 0; flex: 1; background: #2a3942; }
        .list-box { padding: 15px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 10px; }
        .card { background: #111b21; padding: 12px 15px; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; border-left: 4px solid #38bdf8; cursor: pointer; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; background: #374151; display: flex; align-items: center; justify-content: center; font-weight: bold; overflow: hidden; }
        .avatar img { width: 100%; height: 100%; object-fit: cover; }
    </style>
</head>
<body>
    <div class="header">❄️ Frost Pro</div>
    <div class="container">
        <div id="auth">
            <h2>Frost Pro</h2>
            <input type="text" id="username" placeholder="Enter your username">
            <button onclick="connect()">Connect & Get Number</button>
        </div>
        <div class="app" id="app">
            <div class="tab-content active" id="tab-chat">
                <div style="background: #111b21; padding: 8px 15px; font-size: 0.8rem; color: #38bdf8; border-bottom: 1px solid #2a3942; display: flex; justify-content: space-between; align-items: center;">
                    <span id="chatTitle">🌐 General Room (300+ Users)</span>
                    <button onclick="switchTab('dms')" style="width:auto; padding:3px 8px; margin:0; font-size:0.75rem; background:#2a3942;">Switch Chat</button>
                </div>
                <div class="messages" id="stream"></div>
                <div id="preview" style="padding: 4px 15px; font-size: 0.75rem; color: #38bdf8; background:#111b21; display:none;">Image Attached ✓</div>
                <div class="input-bar">
                    <label style="cursor:pointer; font-size:1.2rem;">📷<input type="file" id="imgInput" accept="image/*" style="display:none;" onchange="previewImg(this)"></label>
                    <input type="text" id="msgText" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
                    <button onclick="sendMsg()" style="width:40px; height:40px; border-radius:50%; padding:0; display:flex; align-items:center; justify-content:center;">➤</button>
                </div>
            </div>
            <div class="tab-content" id="tab-dms">
                <div class="list-box">
                    <h3 style="color:#38bdf8; margin:0;">1-to-1 DMs & Lookup</h3>
                    <div style="background:#111b21; padding:12px; border-radius:10px;">
                        <input type="text" id="lookupNum" placeholder="Enter Virtual # (e.g. +1 ...)" style="margin-top:0;">
                        <button onclick="lookupChat()" style="margin-top:8px;">Start Private Chat</button>
                    </div>
                    <div class="card" onclick="openChat('general', '🌐 General Room (300+ Users)')">
                        <div><strong>General Room (300+ Users)</strong><br><span style="font-size:0.75rem; color:#8696a0;">Public Lobby</span></div>
                        <button style="width:auto; padding:5px 10px; margin:0; font-size:0.75rem;">Open</button>
                    </div>
                    <div id="userList"></div>
                </div>
            </div>
            <div class="tab-content" id="tab-settings">
                <div class="list-box">
                    <h3 style="color:#38bdf8; margin:0;">Settings</h3>
                    <div style="background:#111b21; padding:15px; border-radius:10px; display:flex; align-items:center; gap:15px;">
                        <div class="avatar" id="myAvatar">U</div>
                        <div><strong id="myName"></strong><br><span id="myNum" style="color:#38bdf8; font-size:0.8rem;"></span></div>
                    </div>
                    <div style="background:#111b21; padding:15px; border-radius:10px;">
                        <label style="cursor:pointer; display:block; text-align:center; background:#2a3942; padding:10px; border-radius:8px; color:#38bdf8; font-weight:bold;">
                            Upload Profile Picture <input type="file" accept="image/*" style="display:none;" onchange="updateAvatar(this)">
                        </label>
                    </div>
                </div>
            </div>
            <div class="nav">
                <button class="nav-btn active" id="nav-chat" onclick="switchTab('chat')">💬 Chat Room</button>
                <button class="nav-btn" id="nav-dms" onclick="switchTab('dms')">👤 1-to-1 DMs</button>
                <button class="nav-btn" id="nav-settings" onclick="switchTab('settings')">⚙️ Settings</button>
            </div>
        </div>
    </div>
    <script>
        let me = "", myNumber = "", recipient = "general", base64Img = "", usersCache = {};
        function connect() {
            me = document.getElementById('username').value.trim();
            if(!me) return alert("Enter username!");
            fetch('/api/connect', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username: me})})
            .then(res => res.json()).then(data => {
                myNumber = data.virtual_number;
                document.getElementById('auth').style.display = 'none';
                document.getElementById('app').style.display = 'flex';
                document.getElementById('myName').innerText = me;
                document.getElementById('myNum').innerText = "Virtual #: " + myNumber;
                if(data.profile_pic) document.getElementById('myAvatar').innerHTML = '<img src="'+data.profile_pic+'">';
                else document.getElementById('myAvatar').innerText = me.charAt(0).toUpperCase();
                poll(); setInterval(poll, 3000);
            });
        }
        function switchTab(t) {
            ['chat','dms','settings'].forEach(x => {
                document.getElementById('tab-'+x).classList.remove('active');
                document.getElementById('nav-'+x).classList.remove('active');
            });
            document.getElementById('tab-'+t).classList.add('active');
            document.getElementById('nav-'+t).classList.add('active');
            if(t === 'dms') loadUsers();
        }
        function openChat(rcp, title) {
            recipient = rcp;
            document.getElementById('chatTitle').innerText = title;
            switchTab('chat');
            poll();
        }
        function lookupChat() {
            let num = document.getElementById('lookupNum').value.trim();
            let found = "";
            for(let u in usersCache) {
                if(usersCache[u].virtual_number.trim() === num) { found = u; break; }
            }
            if(!found) return alert("User not found with number: " + num);
            if(found === me) return alert("Cannot chat yourself!");
            openChat(found, "💬 1-to-1: " + found + " (" + num + ")");
            document.getElementById('lookupNum').value = "";
        }
        function loadUsers() {
            fetch('/api/users').then(res => res.json()).then(users => {
                usersCache = users;
                let html = "";
                for(let u in users) {
                    if(u === me) continue;
                    let av = users[u].profile_pic ? '<img src="'+users[u].profile_pic+'">' : u.charAt(0).toUpperCase();
                    html += `<div class="card" onclick="openChat('${u}', '💬 1-to-1: ${u}')">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div class="avatar">${av}</div>
                            <div><strong>${u}</strong><br><span style="font-size:0.75rem; color:#38bdf8;">${users[u].virtual_number}</span></div>
                        </div>
                        <button style="width:auto; padding:5px 10px; margin:0; font-size:0.75rem;">Chat</button>
                    </div>`;
                }
                document.getElementById('userList').innerHTML = html;
            });
        }
        function previewImg(input) {
            if(input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = e => { base64Img = e.target.result; document.getElementById('preview').style.display = 'block'; };
                reader.readAsDataURL(input.files[0]);
            }
        }
        function updateAvatar(input) {
            if(input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = e => {
                    fetch('/api/profile_pic', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:me, image:e.target.result})})
                    .then(() => { document.getElementById('myAvatar').innerHTML = '<img src="'+e.target.result+'">'; alert("Updated!"); });
                };
                reader.readAsDataURL(input.files[0]);
            }
        }
        function sendMsg() {
            let txt = document.getElementById('msgText').value.trim();
            if(!txt && !base64Img) return;
            fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:me, recipient:recipient, text:txt, image:base64Img})})
            .then(() => { document.getElementById('msgText').value = ""; base64Img = ""; document.getElementById('preview').style.display = 'none'; poll(); });
        }
        function poll() {
            if(!me) return;
            fetch('/api/chats').then(res => res.json()).then(chats => {
                let stream = document.getElementById('stream');
                let filtered = chats.filter(m => {
                    if(recipient === 'general') return !m.recipient || m.recipient === 'general';
                    return (m.username === me && m.recipient === recipient) || (m.username === recipient && m.recipient === me);
                });
                stream.innerHTML = filtered.map(m => {
                    let isMe = m.username === me;
                    return `<div class="msg ${isMe ? 'sent' : 'received'}">
                        ${!isMe ? '<strong style="color:#38bdf8; font-size:0.75rem; display:block;">'+m.username+'</strong>' : ''}
                        ${m.text ? '<div>'+m.text+'</div>' : ''}
                        ${m.image ? '<img src="'+m.image+'">' : ''}
                        <div style="font-size:0.65rem; color:#bae6fd; text-align:right; margin-top:3px;">${m.time.split(' ')[1].substring(0,5)} ${isMe ? '✓✓' : ''}</div>
                    </div>`;
                }).join('');
                stream.scrollTop = stream.scrollHeight;
            });
        }
    </script>
</body>
</html>
"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        elif self.path == '/api/chats':
            db = db_load()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(db["chats"]).encode('utf-8'))
        elif self.path == '/api/users':
            db = db_load()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(db["users"]).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
        db = db_load()

        if self.path == '/api/connect':
            u = data.get("username")
            if u not in db["users"]:
                db["users"][u] = {"virtual_number": f"+1 ({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}", "profile_pic": ""}
                db_save(db)
            res = db["users"][u]
            res["username"] = u
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))
        elif self.path == '/api/profile_pic':
            u, img = data.get("username"), data.get("image")
            if u in db["users"]:
                db["users"][u]["profile_pic"] = img
                db_save(db)
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
            db_save(db)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

if __name__ == '__main__':
    http.server.HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
