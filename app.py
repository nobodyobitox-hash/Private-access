import http.server, json, os, random
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
DB = "frost.json"

def load():
    if not os.path.exists(DB): return {"users": {}, "chats": []}
    try:
        with open(DB) as f: return json.load(f)
    except: return {"users": {}, "chats": []}

def save(d):
    with open(DB, "w") as f: json.dump(d, f)

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Frost Messenger</title>
<style>
* { box-sizing: border-box; }
body { background: #0b141a; color: #e9edef; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100dvh; overflow: hidden; }
.header { background: #202c33; padding: 12px 20px; font-weight: bold; color: #00a884; display: flex; justify-content: space-between; align-items: center; }
.container { flex: 1; display: flex; flex-direction: column; max-width: 600px; width: 100%; margin: 0 auto; overflow: hidden; }
#auth { padding: 40px 20px; text-align: center; margin: auto; background: #111b21; border-radius: 12px; width: 90%; max-width: 380px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
input, button { width: 100%; padding: 12px; margin-top: 12px; background: #2a3942; color: #fff; border: none; border-radius: 8px; font-size: 0.95rem; }
button { background: #00a884; font-weight: bold; cursor: pointer; }
button:hover { background: #008f72; }
.app { display: none; flex-direction: column; height: 100%; overflow: hidden; }
.messages { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; background: #0b141a; }
.msg { max-width: 75%; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; word-break: break-all; }
.msg.sent { background: #005c4b; align-self: flex-end; }
.msg.received { background: #202c33; align-self: flex-start; }
.input-bar { background: #202c33; padding: 10px 15px; display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.input-bar input { margin: 0; flex: 1; background: #2a3942; }
</style>
</head>
<body onload="checkSaved()">
<div class="header"><span>❄️ Frost Messenger</span><span id="badge" style="font-size:0.75rem; color:#8696a0;"></span></div>
<div class="container">
<div id="auth">
<h2>Frost Messenger</h2>
<p style="font-size:0.8rem; color:#8696a0; margin-bottom:15px;">Enter your username to log in instantly</p>
<input type="text" id="username" placeholder="Your Username">
<button onclick="connect()">Start Chatting</button>
</div>
<div class="app" id="app">
<div style="background:#111b21; padding:8px 15px; font-size:0.8rem; color:#00a884; border-bottom:1px solid #2a3942;">🌐 General Lobby</div>
<div class="messages" id="stream"></div>
<div class="input-bar">
<input type="text" id="msgText" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMsg()">
<button onclick="sendMsg()" style="width:40px; height:40px; border-radius:50%; padding:0; display:flex; align-items:center; justify-content:center;">➤</button>
</div></div></div>
<script>
let me="", myNum="";
function checkSaved() {
    let saved = localStorage.getItem('frost_user');
    if(saved) {
        document.getElementById('username').value = saved;
        connect(saved);
    }
}
function connect(override) {
    let u = override || document.getElementById('username').value.trim();
    if(!u) return alert("Enter a username!");
    
    fetch('/api/connect', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: u})
    }).then(r => r.json()).then(d => {
        me = d.username;
        myNum = d.virtual_number;
        localStorage.setItem('frost_user', me);
        document.getElementById('auth').style.display = 'none';
        document.getElementById('app').style.display = 'flex';
        document.getElementById('badge').innerText = myNum;
        poll(); setInterval(poll, 3000);
    }).catch(err => {
        alert("Connection error: " + err);
    });
}
function sendMsg() {
    let t = document.getElementById('msgText').value.trim();
    if(!t) return;
    fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:me, text:t})})
    .then(()=>{ document.getElementById('msgText').value=""; poll(); });
}
function poll() {
    if(!me) return;
    fetch('/api/chats').then(r=>r.json()).then(chats=>{
        let stream = document.getElementById('stream');
        stream.innerHTML = chats.map(m => {
            let isMe = m.username === me;
            return `<div class="msg ${isMe?'sent':'received'}">${!isMe?'<strong style="color:#00a884; display:block; font-size:0.75rem;">'+m.username+'</strong>':''}${m.text}</div>`;
        }).join('');
        stream.scrollTop = stream.scrollHeight;
    });
}
</script></body></html>
"""

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(200); self.end_headers(); self.wfile.write(HTML.encode())
        elif self.path == '/api/chats':
            d = load()
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(d["chats"]).encode())
        else: self.send_response(404); self.end_headers()

    def do_POST(self):
        l = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(l).decode()) if l else {}
        d = load()
        if self.path == '/api/connect':
            u = data.get("username", "").strip()
            if not u:
                self.send_response(400); self.end_headers(); self.wfile.write(b'{"error":"Invalid username"}'); return
            if u not in d["users"]:
                d["users"][u] = {"virtual_number": f"+1 ({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}"}
            save(d)
            res = d["users"][u].copy(); res["username"] = u
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps(res).encode())
        elif self.path == '/api/chat':
            d["chats"].append({
                "username": data.get("username"),
                "text": data.get("text", ""),
                "time": str(datetime.now())
            })
            save(d)
            self.send_response(200); self.end_headers(); self.wfile.write(b'ok')

if __name__ == '__main__':
    http.server.HTTPServer(('0.0.0.0', PORT), H).serve_forever()
