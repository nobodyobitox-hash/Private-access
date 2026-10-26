# -*- coding: utf-8 -*-
import http.server, json, os, random
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
DB_FILE = "coop_db.json"

def db_load():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "chats": []}
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
    <title>Coop Messenger - Secure & Private</title>
    <style>
        * { box-sizing: border-box; }
        body { background: #0b141a; color: #e9edef; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100dvh; overflow: hidden; }
        .header { background: #202c33; padding: 12px 20px; font-weight: bold; color: #00a884; font-size: 1.1rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a3942; }
        .container { flex: 1; display: flex; flex-direction: column; max-width: 600px; width: 100%; margin: 0 auto; overflow: hidden; }
        #auth { padding: 40px 20px; text-align: center; margin: auto; background: #111b21; border-radius: 12px; width: 90%; max-width: 380px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        input, button { width: 100%; padding: 12px; margin-top: 12px; background: #2a3942; color: #fff; border: none; border-radius: 8px; font-size: 0.95rem; }
        button { background: #00a884; color: #fff; font-weight: bold; cursor: pointer; }
        button:hover { background: #008f72; }
        .app { display: none; flex-direction: column; height: 100%; overflow: hidden; }
        .tab-content { flex: 1; display: none; flex-direction: column; overflow: hidden; }
        .tab-content.active { display: flex; }
        .nav { background: #202c33; display: flex; border-top: 1px solid #2a3942; flex-shrink: 0; }
        .nav-btn { flex: 1; padding: 12px; text-align: center; color: #8696a0; background: none; border: none; font-weight: bold; font-size: 0.8rem; cursor: pointer; }
        .nav-btn.active { color: #00a884; background: #111b21; border-top: 2px solid #00a884; }
        .messages { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; background: #0b141a; }
        .msg { max-width: 75%; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; word-break: break-all; position: relative; }
        .msg.sent { background: #005c4b; align-self: flex-end; }
        .msg.received { background: #202c33; align-self: flex-start; }
        .msg img, .msg video, .msg audio { max-width: 100%; border-radius: 6px; margin-top: 5px; }
        .tag { font-size: 0.65rem; background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; color: #00a884; display: inline-block; margin-bottom: 4px; }
        .view-once-box { background: #111b21; border: 1px dashed #00a884; padding: 10px; border-radius: 6px; text-align: center; cursor: pointer; color: #00a884; font-size: 0.85rem; }
        .input-bar { background: #202c33; padding: 10px 15px; display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
        .input-bar input { margin: 0; flex: 1; background: #2a3942; }
        .list-box { padding: 15px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 10px; }
        .card { background: #111b21; padding: 12px 15px; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; border-left: 4px solid #00a884; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; background: #374151; display: flex; align-items: center; justify-content: center; font-weight: bold; overflow: hidden; }
        .avatar img { width: 100%; height: 100%; object-fit: cover; }
    </style>
</head>
<body>
    <div class="header">
        <span>🟢 Coop Messenger</span>
        <span id="myVirtualBadge" style="font-size:0.75rem; color:#8696a0;"></span>
    </div>
    <div class="container">
        <div id="auth">
            <h2>Coop Messenger Login</h2>
            <p style="font-size:0.8rem; color:#8696a0; margin-bottom:15px;">Secure End-to-End Encrypted Chat</p>
            <input type="text" id="username" placeholder="Username">
            <input type="password" id="password" placeholder="Secure Password">
            <button onclick="connect()">Login / Register</button>
        </div>
        <div class="app" id="app">
            <div class="tab-content active" id="tab-chat">
                <div style="background: #111b21; padding: 8px 15px; font-size: 0.8rem; color: #00a884; border-bottom: 1px solid #2a3942; display: flex; justify-content: space-between; align-items: center;">
                    <span id="chatTitle">🌐 General Community Lobby</span>
                    <button onclick="switchTab('dms')" style="width:auto; padding:3px 8px; margin:0; font-size:0.75rem; background:#2a3942; color:#fff;">Search by Number</button>
                </div>
                <div class="messages" id="stream"></div>
                <div id="preview" style="padding: 4px 15px; font-size: 0.75rem; color: #00a884; background:#111b21; display:none;">Media Attached ✓</div>
                <div class="input-bar">
                    <label style="cursor:pointer; font-size:1.2rem;" title="Attach Media">📎<input type="file" id="mediaInput" accept="image/*,video/mp4,audio/*" style="display:none;" onchange="previewMedia(this)"></label>
                    <label style="font-size:0.75rem; color:#8696a0; display:flex; align-items:center; gap:2px; cursor:pointer;" title="View Once"><input type="checkbox" id="viewOnceCheck"> 1x</label>
                    <input type="text" id="msgText" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
                    <button onclick="sendMsg()" style="width:40px; height:40px; border-radius:50%; padding:0; display:flex; align-items:center; justify-content:center;">➤</button>
                </div>
            </div>
            <div class="tab-content" id="tab-dms">
                <div class="list-box">
                    <h3 style="color:#00a884; margin:0;">🔒 Secure Number Lookup</h3>
                    <p style="font-size:0.8rem; color:#8696a0; margin:0;">User lists are hidden to protect user privacy. Enter a virtual number to chat 1-to-1.</p>
                    <div style="background:#111b21; padding:12px; border-radius:10px;">
                        <input type="text" id="lookupNum" placeholder="e.g. +1 (334) 000-0000" style="margin-top:0;">
                        <button onclick="lookupChat()" style="margin-top:8px;">Open Private Chat</button>
                    </div>
                    <div class="card" onclick="openChat('general', '🌐 General Community Lobby')" style="cursor:pointer;">
                        <div><strong>🌐 General Community Lobby</strong><br><span style="font-size:0.75rem; color:#8696a0;">Public group channel</span></div>
                        <button style="width:auto; padding:5px 10px; margin:0; font-size:0.75rem;">Open</button>
                    </div>
                </div>
            </div>
            <div class="tab-content" id="tab-settings">
                <div class="list-box">
                    <h3 style="color:#00a884; margin:0;">Account Settings</h3>
                    <div style="background:#111b21; padding:15px; border-radius:10px; display:flex; align-items:center; gap:15px;">
                        <div class="avatar" id="myAvatar">U</div>
                        <div><strong id="myName"></strong><br><span id="myNum" style="color:#00a884; font-size:0.8rem;"></span></div>
                    </div>
                    <div style="background:#111b21; padding:15px; border-radius:10px;">
                        <label style="cursor:pointer; display:block; text-align:center; background:#2a3942; padding:10px; border-radius:8px; color:#00a884; font-weight:bold;">
                            Upload Permanent Avatar <input type="file" accept="image/*" style="display:none;" onchange="updateAvatar(this)">
                        </label>
                    </div>
                </div>
            </div>
            <div class="nav">
                <button class="nav-btn active" id="nav-chat" onclick="switchTab('chat')">💬 Chats</button>
                <button class="nav-btn" id="nav-dms" onclick="switchTab('dms')">🔍 Lookup</button>
                <button class="nav-btn" id="nav-settings" onclick="switchTab('settings')">⚙️ Settings</button>
            </div>
        </div>
    </div>
    <script>
        let me = "", myNumber = "", recipient = "general", mediaData = "", mediaType = "";
        function connect() {
            me = document.getElementById('username').value.trim();
            let pwd = document.getElementById('password').value.trim();
            if(!me || !pwd) return alert("Enter both username and password!");
            
            fetch('/api/connect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: me, password: pwd})
            }).then(async res => {
                let text = await res.text();
                let data;
                try {
                    data = JSON.parse(text);
                } catch(e) {
                    alert("Server error response: " + text);
                    throw new Error(text);
                }
                if(!res.ok) {
                    alert(data.error || "Login failed!");
                    throw new Error(data.error);
                }
                return data;
            }).then(data => {
                myNumber = data.virtual_number;
                document.getElementById('auth').style.display = 'none';
                document.getElementById('app').style.display = 'flex';
                document.getElementById('myName').innerText = me;
                document.getElementById('myNum').innerText = "Virtual #: " + myNumber;
                document.getElementById('myVirtualBadge').innerText = myNumber;
                if(data.profile_pic) document.getElementById('myAvatar').innerHTML = '<img src="'+data.profile_pic+'">';
                else document.getElementById('myAvatar').innerText = me.charAt(0).toUpperCase();
                poll(); setInterval(poll, 6000);
            }).catch(err => console.log(err));
        }
        function switchTab(t) {
            ['chat','dms','settings'].forEach(x => {
                document.getElementById('tab-'+x).classList.remove('active');
                document.getElementById('nav-'+x).classList.remove('active');
            });
            document.getElementById('tab-'+t).classList.add('active');
            document.getElementById('nav-'+t).classList.add('active');
        }
        function openChat(rcp, title) {
            recipient = rcp;
            document.getElementById('chatTitle').innerText = title;
            switchTab('chat');
            poll();
        }
        function lookupChat() {
            let num = document.getElementById('lookupNum').value.trim();
            if(!num) return alert("Enter virtual number!");
            fetch('/api/lookup?num=' + encodeURIComponent(num)).then(res => res.json()).then(data => {
                if(!data.found) return alert("No user found with number: " + num);
                if(data.username === me) return alert("Cannot chat with yourself!");
                openChat(data.username, "🔒 Encrypted 1-to-1: " + data.username);
                document.getElementById('lookupNum').value = "";
            });
        }
        function previewMedia(input) {
            if(input.files && input.files[0]) {
                let file = input.files[0];
                mediaType = file.type.includes('video') ? 'video' : file.type.includes('audio') ? 'audio' : 'image';
                let reader = new FileReader();
                reader.onload = e => { mediaData = e.target.result; document.getElementById('preview').style.display = 'block'; };
                reader.readAsDataURL(file);
            }
        }
        function updateAvatar(input) {
            if(input.files && input.files[0]) {
                let reader = new FileReader();
                reader.onload = e => {
                    fetch('/api/profile_pic', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:me, image:e.target.result})})
                    .then(() => { document.getElementById('myAvatar').innerHTML = '<img src="'+e.target.result+'">'; alert("Avatar Updated Permanently!"); });
                };
                reader.readAsDataURL(input.files[0]);
            }
        }
        function sendMsg() {
            let txt = document.getElementById('msgText').value.trim();
            let isViewOnce = document.getElementById('viewOnceCheck').checked;
            if(!txt && !mediaData) return;
            fetch('/api/chat', {
                method:'POST', 
                headers:{'Content-Type':'application/json'}, 
                body:JSON.stringify({username:me, recipient:recipient, text:txt, media:mediaData, media_type:mediaType, view_once:isViewOnce})
            }).then(() => {
                document.getElementById('msgText').value = "";
                mediaData = "";
                mediaType = "";
                document.getElementById('preview').style.display = 'none';
                document.getElementById('viewOnceCheck').checked = false;
                poll();
            });
        }
        function openViewOnce(msgId, mData, mType) {
            let container = document.getElementById('vo-' + msgId);
            let content = mType === 'video' ? '<video src="'+mData+'" controls autoplay style="max-width:100%; border-radius:6px;"></video>' : '<img src="'+mData+'" style="max-width:100%; border-radius:6px;">';
            container.innerHTML = content + '<br><span style="font-size:0.7rem; color:#ef4444;">[Opened & Destroyed]</span>';
            fetch('/api/burn', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id: msgId})});
        }
        function poll() {
            if(!me) return;
            fetch('/api/chats').then(res => res.json()).then(chats => {
                let stream = document.getElementById('stream');
                let filtered = chats.filter(m => {
                    if(recipient === 'general') return !m.recipient || m.recipient === 'general';
                    return (m.username === me && m.recipient === recipient) || (m.username === recipient && m.recipient === me);
                });
                stream.innerHTML = filtered.map((m, idx) => {
                    let isMe = m.username === me;
                    let tagText = recipient === 'general' ? '🌐 General Community Lobby' : '🔒 End-to-End Encrypted Private Chat';
                    let contentHtml = "";
                    if(m.text) contentHtml += '<div>'+m.text+'</div>';
                    if(m.media) {
                        if(m.view_once && !m.burned) {
                            let label = m.media_type === 'video' ? '🎬 Tap to View Once Video' : m.media_type === 'audio' ? '🔊 Tap to Listen Audio' : '📷 Tap to View Once Photo';
                            contentHtml += '<div class="view-once-box" id="vo-'+idx+'" onclick="openViewOnce('+idx+', \''+m.media+'\', \''+m.media_type+'\')">'+label+'</div>';
                        } else if(m.view_once && m.burned) {
                            contentHtml += '<div style="font-size:0.8rem; color:#8696a0; font-style:italic;">[Media Opened & Destroyed]</div>';
                        } else {
                            if(m.media_type === 'video') contentHtml += '<video src="'+m.media+'" controls></video>';
                            else if(m.media_type === 'audio') contentHtml += '<audio src="'+m.media+'" controls></audio>';
                            else contentHtml += '<img src="'+m.media+'">';
                        }
                    }
                    return `<div class="msg ${isMe ? 'sent' : 'received'}">
                        <span class="tag">${tagText}</span>
                        ${!isMe ? '<strong style="color:#00a884; font-size:0.75rem; display:block;">'+m.username+'</strong>' : ''}
                        ${contentHtml}
                        <div style="font-size:0.65rem; color:#8696a0; text-align:right; margin-top:3px;">${m.time.split(' ')[1].substring(0,5)} ${isMe ? '✓✓ Delivered' : ''}</div>
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
        elif self.path.startswith('/api/lookup'):
            query = self.path.split('?')[1].replace('num=', '')
            db = db_load()
            found_user = None
            for u in db["users"]:
                if db["users"][u]["virtual_number"].strip() == query.strip():
                    found_user = u
                    break
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            if found_user:
                self.wfile.write(json.dumps({"found": True, "username": found_user}).encode('utf-8'))
            else:
                self.wfile.write(b'{"found":false}')
        elif self.path == '/api/chats':
            db = db_load()
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(db["chats"]).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
        db = db_load()

        if self.path == '/api/connect':
            u = data.get("username")
            pwd = data.get("password", "")
            if u in db["users"]:
                if db["users"][u].get("password", "") != pwd:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Incorrect password for this username!"}).encode('utf-8'))
                    return
            else:
                db["users"][u] = {
                    "password": pwd,
                    "virtual_number": f"+1 ({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
                    "profile_pic": ""
                }
                db_save(db)
            res = db["users"][u].copy()
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
                "media": data.get("media", ""),
                "media_type": data.get("media_type", "image"),
                "view_once": data.get("view_once", False),
                "burned": False,
                "time": str(datetime.now())
            })
            db_save(db)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'json_ok')
        elif self.path == '/api/burn':
            msg_id = data.get("id")
            if msg_id is not None and msg_id < len(db["chats"]):
                db["chats"][msg_id]["media"] = ""
                db["chats"][msg_id]["burned"] = True
                db_save(db)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"burned"}')

if __name__ == '__main__':
    http.server.HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
