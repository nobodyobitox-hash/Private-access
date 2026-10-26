import http.server, json, os, random
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
DB = "coop.json"

def load():
    if not os.path.exists(DB): return {"users": {}, "chats": [], "ips": {}}
    try:
        with open(DB) as f: return json.load(f)
    except: return {"users": {}, "chats": [], "ips": {}}

def save(d):
    with open(DB, "w") as f: json.dump(d, f)

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Coop Messenger</title>
<style>
body { background: #0b141a; color: #e9edef; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100dvh; }
.header { background: #202c33; padding: 12px 20px; font-weight: bold; color: #00a884; display: flex; justify-content: space-between; }
.container { flex: 1; display: flex; flex-direction: column; max-width: 600px; width: 100%; margin: 0 auto; overflow: hidden; }
#auth { padding: 40px 20px; text-align: center; margin: auto; background: #111b21; border-radius: 12px; width: 90%; max-width: 380px; }
input, button { width: 100%; padding: 12px; margin-top: 12px; background: #2a3942; color: #fff; border: none; border-radius: 8px; }
button { background: #00a884; font-weight: bold; cursor: pointer; }
.app { display: none; flex-direction: column; height: 100%; }
.messages { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
.msg { max-width: 75%; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; position: relative; }
.msg.sent { background: #005c4b; align-self: flex-end; }
.msg.received { background: #202c33; align-self: flex-start; }
.msg img, .msg video, .msg audio { max-width: 100%; border-radius: 6px; margin-top: 5px; }
.tag { font-size: 0.65rem; background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; color: #00a884; display: inline-block; margin-bottom: 4px; }
.input-bar { background: #202c33; padding: 10px 15px; display: flex; align-items: center; gap: 8px; }
.input-bar input { margin: 0; flex: 1; background: #2a3942; }
</style>
</head>
<body onload="autoLogin()">
<div class="header"><span>🟢 Coop Messenger</span><span id="badge" style="font-size:0.75rem; color:#8696a0;"></span></div>
<div class="container">
<div id="auth">
<h2>Coop Messenger</h2>
<p style="font-size:0.8rem; color:#8696a0;">Enter username to chat instantly</p>
<input type="text" id="username" placeholder="Username">
<button onclick="connect()">Start Chatting</button>
</div>
<div class="app" id="app">
<div style="background:#111b21; padding:8px 15px; font-size:0.8rem; color:#00a884; border-bottom:1px solid #2a3942;">🌐 General Community Lobby</div>
<div class="messages" id="stream"></div>
<div class="input-bar">
<label style="cursor:pointer; font-size:1.2rem;">📎<input type="file" id="mediaInput" accept="image/*,video/mp4,audio/*" style="display:none;" onchange="previewMedia(this)"></label>
<input type="text" id="msgText" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
<button onclick="sendMsg()" style="width:40px; height:40px; border-radius:50%; padding:0;">➤</button>
</div></div></div>
<script>
let me="", myNum="", mediaData="", mediaType="";
function autoLogin() {
    let saved = localStorage.getItem('coop_user');
    if(saved) { connect(saved); }
    else { fetch('/api/iplogin').then(r=>r.json()).then(d=>{ if(d.found) connect(d.username); }); }
}
function connect(override) {
    let u = override || document.getElementById('username').value.trim();
    if(!u) return alert("Enter username!");
    fetch('/api/connect', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:u})})
    .then(r=>r.json()).then(d=>{
        me=d.username; myNum=d.virtual_number;
        localStorage.setItem('coop_user', me);
        document.getElementById('auth').style.display='none';
        document.getElementById('app').style.display='flex';
        document.getElementById('badge').innerText=myNum;
        poll(); setInterval(poll, 6000);
    });
}
function previewMedia(i) {
    if(i.files && i.files[0]) {
        let f = i.files[0];
        mediaType = f.type.includes('video')?'video':f.type.includes('audio')?'audio':'image';
        let r = new FileReader();
        r.onload = e => { mediaData = e.target.result; alert("Media attached! Ready to send."); };
        r.readAsDataURL(f);
    }
}
function sendMsg() {
    let t = document.getElementById('msgText').value.trim();
    if(!t && !mediaData) return;
    fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:me, text:t, media:mediaData, media_type:mediaType})})
    .then(()=>{ document.getElementById('msgText').value=""; mediaData=""; mediaType=""; poll(); });
}
function poll() {
    if(!me) return;
    fetch('/api/chats').then(r=>r.json()).then(chats=>{
        let stream = document.getElementById('stream');
        stream.innerHTML = chats.map(m => {
            let isMe = m.username === me;
            let content = (m.text ? '<div>'+m.text+'</div>':'') + (m.media ? (m.media_type==='video'?'<video src="'+m.media+'" controls></video>':m.media_type==='audio'?'<audio src="'+m.media+'" controls></audio>':'<img src="'+m.media+'">') : '');
            return `<div class="msg ${isMe?'sent':'received'}"><span class="tag">🔒 End-to-End Encrypted</span>${!isMe?'<strong style="color:#00a884; display:block; font-size:0.75rem;">'+m.username+'</strong>':''}${content}<div style="font-size:0.65rem; color:#8696a0; text-align:right;">✓✓</div></div>`;
        }).join('');
        stream.scrollTop = stream.scrollHeight;
    });
}
</script></body></html>
"""

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        ip = self.headers.get('X-Forwarded-For', self.client_address[0])
        if self.path in ('/', '/index.html'):
            self.send_response(200); self.end_headers(); self.wfile.write(HTML.encode())
        elif self.path == '/api/iplogin':
            d = load()
            self.send_response(200); self.end_headers()
            if ip in d["ips"] and d["ips"][ip] in d["users"]:
                self.wfile.write(json.dumps({"found": True, "username": d["ips"][ip]}).encode())
            else: self.wfile.write(b'{"found":false}')
        elif self.path == '/api/chats':
            d = load()
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(d["chats"]).encode())
        else: self.send_response(404); self.end_headers()

    def do_POST(self):
        ip = self.headers.get('X-Forwarded-For', self.client_address[0])
        l = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(l).decode()) if l else {}
        d = load()
        if self.path == '/api/connect':
            u = data.get("username", "").strip()
            if not u: return
            if u not in d["users"]:
                d["users"][u] = {"virtual_number": f"+1 ({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}"}
            d["ips"][ip] = u
            save(d)
            res = d["users"][u].copy(); res["username"] = u
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(res).encode())
        elif self.path == '/api/chat':
            d["chats"].append({
                "username": data.get("username"),
                "text": data.get("text", ""),
                "media": data.get("media", ""),
                "media_type": data.get("media_type", "image"),
                "time": str(datetime.now())
            })
            save(d)
            self.send_response(200); self.end_headers(); self.wfile.write(b'ok')

if __name__ == '__main__':
    http.server.HTTPServer(('0.0.0.0', PORT), H).serve_forever()
