import http.server, json, os, random
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
DB_FILE = "mythic_db.json"

def db_load():
    if not os.path.exists(DB_FILE):
        return {"players": {}, "chats": []}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except:
        return {"players": {}, "chats": []}

def db_save(d):
    with open(DB_FILE, "w") as f: json.dump(d, f)

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Mythic Realms: Ancient Creek Methodist</title>
<style>
* { box-sizing: border-box; touch-action: none; user-select: none; -webkit-user-select: none; }
body, html { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #080c10; font-family: sans-serif; color: #e2e8f0; }
#gameContainer { position: relative; width: 100vw; height: 100vh; background: #0b131b; }
canvas { display: block; width: 100%; height: 100%; }
.top-hud { position: absolute; top: 10px; left: 10px; right: 10px; display: flex; justify-content: space-between; align-items: center; pointer-events: none; z-index: 10; }
.hud-card { background: rgba(15, 23, 42, 0.85); border: 1px solid #3b82f6; border-radius: 8px; padding: 8px 14px; backdrop-filter: blur(4px); pointer-events: auto; }
.player-info { display: flex; align-items: center; gap: 10px; }
.avatar { width: 36px; height: 36px; border-radius: 50%; background: #2563eb; border: 2px solid #60a5fa; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; }
.bar-container { width: 120px; height: 10px; background: #1e293b; border-radius: 5px; overflow: hidden; margin-top: 3px; border: 1px solid #475569; }
.hp-bar { width: 100%; height: 100%; background: linear-gradient(90deg, #ef4444, #f87171); transition: width 0.2s; }
.ult-bar { width: 0%; height: 100%; background: linear-gradient(90deg, #eab308, #fef08a); transition: width 0.2s; }
.touch-hud { position: absolute; inset: 0; pointer-events: none; z-index: 20; }
.interactive { pointer-events: auto; }
#joystickZone { position: absolute; bottom: 30px; left: 30px; width: 140px; height: 140px; background: rgba(255, 255, 255, 0.08); border: 2px solid rgba(255, 255, 255, 0.2); border-radius: 50%; }
#joystickKnob { position: absolute; top: 35px; left: 35px; width: 70px; height: 70px; background: radial-gradient(circle, #3b82f6 0%, #1d4ed8 100%); border-radius: 50%; border: 2px solid #93c5fd; box-shadow: 0 0 15px rgba(59, 130, 246, 0.5); }
.action-cluster { position: absolute; bottom: 25px; right: 25px; width: 220px; height: 220px; }
.btn-action { position: absolute; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; text-shadow: 0 1px 3px rgba(0,0,0,0.8); box-shadow: 0 4px 10px rgba(0,0,0,0.5); border: 2px solid rgba(255,255,255,0.3); }
.btn-action:active { transform: scale(0.92); filter: brightness(1.2); }
#btnPrimary { bottom: 20px; right: 20px; width: 75px; height: 75px; background: linear-gradient(135deg, #ef4444, #991b1b); font-size: 1.1rem; border-color: #fca5a5; }
#btnHeavy { bottom: 95px; right: 25px; width: 55px; height: 55px; background: linear-gradient(135deg, #f97316, #c2410c); font-size: 0.85rem; }
#btnSkill { bottom: 25px; right: 95px; width: 55px; height: 55px; background: linear-gradient(135deg, #a855f7, #6b21a8); font-size: 0.85rem; }
#btnParry { bottom: 145px; right: 75px; width: 45px; height: 45px; background: linear-gradient(135deg, #3b82f6, #1e40af); font-size: 0.75rem; }
#btnDash { bottom: 75px; right: 145px; width: 45px; height: 45px; background: linear-gradient(135deg, #10b981, #065f46); font-size: 0.75rem; }
#btnSwap { position: absolute; top: 65px; right: 15px; width: 50px; height: 50px; border-radius: 50%; background: #334155; border: 2px solid #38bdf8; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 0.7rem; color: #38bdf8; }
#btnUlt { position: absolute; top: 125px; right: 15px; width: 55px; height: 55px; border-radius: 50%; background: linear-gradient(135deg, #eab308, #ca8a04); border: 2px solid #fef08a; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.85rem; color: #000; opacity: 0.5; }
#btnUlt.ready { opacity: 1; }
#loginModal { position: absolute; inset: 0; background: rgba(11, 19, 27, 0.95); z-index: 50; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
.auth-box { background: #1e293b; border: 2px solid #3b82f6; border-radius: 12px; padding: 30px; width: 90%; max-width: 380px; text-align: center; }
.auth-box h1 { color: #60a5fa; margin-top: 0; font-size: 1.5rem; }
.auth-box input, .auth-box select { width: 100%; padding: 12px; margin-bottom: 12px; background: #0f172a; border: 1px solid #334155; color: #fff; border-radius: 8px; }
.auth-box button { width: 100%; padding: 12px; background: #2563eb; color: #fff; border: none; border-radius: 8px; font-weight: bold; font-size: 1rem; cursor: pointer; }
#chatContainer { position: absolute; bottom: 20px; left: 180px; width: 200px; height: 120px; background: rgba(15, 23, 42, 0.7); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); pointer-events: auto; display: flex; flex-direction: column; z-index: 15; }
#chatLogs { flex: 1; overflow-y: auto; padding: 6px; font-size: 0.75rem; color: #cbd5e1; }
#chatInput { background: rgba(0,0,0,0.5); border: none; padding: 6px; color: #fff; font-size: 0.75rem; border-top: 1px solid rgba(255,255,255,0.1); outline: none; }
</style>
</head>
<body>
<div id="gameContainer">
    <canvas id="gameCanvas"></canvas>
    <div class="top-hud">
        <div class="hud-card player-info">
            <div class="avatar" id="hudAvatar">M</div>
            <div>
                <strong id="hudName" style="color:#60a5fa; font-size:0.85rem;">Hero</strong>
                <div style="font-size:0.65rem; color:#94a3b8;">Creek Methodist Ruins</div>
                <div class="bar-container"><div class="hp-bar" id="hudHp"></div></div>
                <div class="bar-container" style="margin-top:2px;"><div class="ult-bar" id="hudUlt"></div></div>
            </div>
        </div>
        <div class="hud-card" style="font-size:0.75rem;">
            <div>🗡️ <span id="hudWeapon">SWORD</span></div>
            <div>👥 Online: <span id="hudOnline" style="color:#10b981;">1</span></div>
        </div>
    </div>
    <div class="touch-hud">
        <div id="btnSwap" class="interactive" onclick="switchWeapon()"><span>SWAP</span><span id="weaponTypeLabel" style="font-size:0.55rem;">SWORD</span></div>
        <div id="btnUlt" class="interactive" onclick="triggerUlt()">ULT</div>
        <div id="joystickZone" class="interactive"><div id="joystickKnob"></div></div>
        <div class="action-cluster">
            <div id="btnPrimary" class="btn-action interactive" onmousedown="handleAction('attack')" ontouchstart="handleAction('attack')">ATK</div>
            <div id="btnHeavy" class="btn-action interactive" onmousedown="handleAction('heavy')" ontouchstart="handleAction('heavy')">HEAVY</div>
            <div id="btnSkill" class="btn-action interactive" onmousedown="handleAction('skill')" ontouchstart="handleAction('skill')">SKILL</div>
            <div id="btnParry" class="btn-action interactive" onmousedown="handleAction('parry')" ontouchstart="handleAction('parry')">PARRY</div>
            <div id="btnDash" class="btn-action interactive" onmousedown="handleAction('dash')" ontouchstart="handleAction('dash')">DASH</div>
        </div>
        <div id="chatContainer">
            <div id="chatLogs">Welcome to Ancient Creek Methodist Ruins!</div>
            <input type="text" id="chatInput" placeholder="Chat..." onkeypress="if(event.key==='Enter') sendChat()">
        </div>
    </div>
    <div id="loginModal">
        <div class="auth-box">
            <h1>Mythic Realms</h1>
            <p>Ancient Creek Methodist Exploration</p>
            <input type="text" id="usernameInput" placeholder="Hero Name">
            <select id="weaponSelect">
                <option value="SWORD">Sword & Shield (Precision)</option>
                <option value="GAUNTLETS">Gauntlets / Fist (Combo Grapple)</option>
                <option value="SPEAR">Spear / Halberd (Reach Sweeps)</option>
            </select>
            <button onclick="startGame()">Enter Ancient Creek</button>
        </div>
    </div>
</div>
<script>
let canvas = document.getElementById('gameCanvas');
let ctx = canvas.getContext('2d');
function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
window.addEventListener('resize', resize); resize();

let me = { id: "", name: "Hero", x: 400, y: 300, hp: 100, maxHp: 100, ult: 0, weapon: "SWORD", facing: "right", animTimer: 0 };
let players = {}, particles = [];
let joystickActive = false, joystickVector = { x: 0, y: 0 };
let enemies = [
    { id: "e1", x: 600, y: 350, hp: 150, maxHp: 150, type: "Creek Guardian" },
    { id: "e2", x: 850, y: 220, hp: 100, maxHp: 100, type: "Methodist Wraith" }
];

function startGame() {
    let u = document.getElementById('usernameInput').value.trim();
    if(!u) return alert("Enter Hero Name!");
    me.name = u; me.weapon = document.getElementById('weaponSelect').value;
    me.id = "hero_" + Math.random().toString(36).substr(2, 6);
    document.getElementById('hudName').innerText = me.name;
    document.getElementById('hudAvatar').innerText = me.name.charAt(0).toUpperCase();
    document.getElementById('hudWeapon').innerText = me.weapon;
    document.getElementById('weaponTypeLabel').innerText = me.weapon;
    document.getElementById('loginModal').style.display = 'none';
    setupJoystick(); connectServer(); requestAnimationFrame(gameLoop);
}

function setupJoystick() {
    let zone = document.getElementById('joystickZone'), knob = document.getElementById('joystickKnob');
    function handleStart(e) { joystickActive = true; updateJoystick(e.touches ? e.touches[0] : e); }
    function handleMove(e) { if(joystickActive) updateJoystick(e.touches ? e.touches[0] : e); }
    function handleEnd() { joystickActive = false; joystickVector = { x: 0, y: 0 }; knob.style.transform = `translate(0px, 0px)`; }
    function updateJoystick(touch) {
        let rect = zone.getBoundingClientRect(), centerX = rect.left + rect.width / 2, centerY = rect.top + rect.height / 2;
        let dx = touch.clientX - centerX, dy = touch.clientY - centerY, dist = Math.hypot(dx, dy), maxDist = rect.width / 2 - 20;
        if (dist > maxDist) { dx = (dx / dist) * maxDist; dy = (dy / dist) * maxDist; }
        knob.style.transform = `translate(${dx}px, ${dy}px)`; joystickVector = { x: dx / maxDist, y: dy / maxDist };
    }
    zone.addEventListener('touchstart', handleStart); window.addEventListener('touchmove', handleMove); window.addEventListener('touchend', handleEnd);
    zone.addEventListener('mousedown', handleStart); window.addEventListener('mousemove', handleMove); window.addEventListener('mouseup', handleEnd);
}

function handleAction(action) {
    if(action === 'attack') {
        me.animTimer = 10; me.ult = Math.min(100, me.ult + 10);
        document.getElementById('hudUlt').style.width = me.ult + '%';
        if(me.ult >= 100) document.getElementById('btnUlt').classList.add('ready');
        let range = me.weapon === 'SPEAR' ? 120 : 70;
        enemies.forEach(e => { if(Math.hypot(e.x - me.x, e.y - me.y) < range) { e.hp -= 25; addParticle(e.x, e.y, "#ef4444", "-25 DMG"); } });
    } else if(action === 'heavy') {
        enemies.forEach(e => { if(Math.hypot(e.x - me.x, e.y - me.y) < 100) { e.hp -= 45; addParticle(e.x, e.y, "#f97316", "-45 HEAVY!"); } });
    } else if(action === 'skill') { addParticle(me.x, me.y, "#a855f7", "MYTHIC SKILL!"); }
    else if(action === 'parry') { addParticle(me.x, me.y, "#3b82f6", "PARRY!"); }
    else if(action === 'dash') { me.x += (joystickVector.x || (me.facing==='right'?1:-1)) * 90; me.y += (joystickVector.y || 0) * 90; addParticle(me.x, me.y, "#10b981", "DASH!"); }
}

function switchWeapon() {
    let w = ["SWORD", "GAUNTLETS", "SPEAR"];
    me.weapon = w[(w.indexOf(me.weapon) + 1) % w.length];
    document.getElementById('hudWeapon').innerText = me.weapon;
    document.getElementById('weaponTypeLabel').innerText = me.weapon;
}
function triggerUlt() {
    if(me.ult < 100) return;
    me.ult = 0; document.getElementById('hudUlt').style.width = '0%'; document.getElementById('btnUlt').classList.remove('ready');
    enemies.forEach(e => { e.hp -= 80; addParticle(e.x, e.y, "#ef4444", "-80 ULT DMG"); });
}
function addParticle(x, y, color, text) { particles.push({ x: x, y: y - 20, color: color, text: text, life: 30 }); }
function connectServer() {
    setInterval(() => {
        fetch('/api/sync', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ me: me }) })
        .then(r => r.json()).then(data => { players = data.players || {}; document.getElementById('hudOnline').innerText = Object.keys(players).length; }).catch(e=>{});
    }, 1000);
}
function sendChat() {
    let i = document.getElementById('chatInput'), t = i.value.trim(); if(!t) return;
    let l = document.getElementById('chatLogs'); l.innerHTML += `<div><strong>${me.name}:</strong> ${t}</div>`; l.scrollTop = l.scrollHeight; i.value = "";
}

function gameLoop() {
    if (joystickActive) {
        me.x += joystickVector.x * 4; me.y += joystickVector.y * 4;
        if (joystickVector.x > 0) me.facing = "right"; if (joystickVector.x < 0) me.facing = "left";
    }
    me.x = Math.max(50, Math.min(canvas.width - 50, me.x)); me.y = Math.max(100, Math.min(canvas.height - 100, me.y));
    ctx.fillStyle = "#0b131b"; ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Ancient Creek Methodist Background
    ctx.fillStyle = "rgba(14, 165, 233, 0.15)"; ctx.fillRect(0, canvas.height * 0.4, canvas.width, 120);
    ctx.fillStyle = "#1e293b"; ctx.fillRect(150, 100, 40, 180); ctx.fillRect(350, 80, 40, 200); ctx.fillRect(750, 120, 40, 160);
    ctx.fillStyle = "#334155"; ctx.font = "bold 16px serif"; ctx.fillText("⛪ ANCIENT CREEK METHODIST RUINS", canvas.width / 2 - 150, 40);

    // Enemies
    enemies.forEach(e => {
        if(e.hp <= 0) return;
        ctx.fillStyle = e.type === "Creek Guardian" ? "#dc2626" : "#7c3aed";
        ctx.beginPath(); ctx.arc(e.x, e.y, 20, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = "#ef4444"; ctx.fillRect(e.x - 25, e.y - 35, (e.hp / e.maxHp) * 50, 6);
    });

    // Players Sync
    for(let pid in players) {
        if(pid === me.id) continue;
        let p = players[pid];
        ctx.fillStyle = "#059669"; ctx.beginPath(); ctx.arc(p.x, p.y, 18, 0, Math.PI * 2); ctx.fill();
    }

    // Player Hero
    ctx.fillStyle = "#2563eb"; ctx.beginPath(); ctx.arc(me.x, me.y, 22, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = "#93c5fd"; ctx.lineWidth = 3; ctx.stroke();
    if(me.animTimer > 0) { me.animTimer--; ctx.strokeStyle = "#f59e0b"; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(me.x, me.y, 45, 0, 3); ctx.stroke(); }

    particles.forEach((p, idx) => { ctx.fillStyle = p.color; ctx.font = "bold 13px sans-serif"; ctx.fillText(p.text, p.x, p.y); p.y -= 1; p.life--; if(p.life <= 0) particles.splice(idx, 1); });
    requestAnimationFrame(gameLoop);
}
</script></body></html>
"""

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(200); self.end_headers(); self.wfile.write(HTML.encode())
        else: self.send_response(404); self.end_headers()
    def do_POST(self):
        l = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(l).decode()) if l else {}
        db = db_load()
        if self.path == '/api/sync':
            m = data.get("me", {})
            if m and "id" in m: db["players"][m["id"]] = m; db_save(db)
            self.send_response(200); self.end_headers(); self.wfile.write(json.dumps({"players": db["players"]}).encode())

if __name__ == '__main__':
    http.server.HTTPServer(('0.0.0.0', PORT), H).serve_forever()
