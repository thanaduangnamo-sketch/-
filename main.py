import os
import json
import threading
import requests
import discord
from discord.ext import commands
from flask import Flask, redirect, url_for, session, request, render_template_string

# ==========================================
# 1. SETTINGS & CONFIGURATION (SECURED)
# ==========================================
CLIENT_ID = os.getenv("CLIENT_ID", "1532644387639660627")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BOT_TOKEN = os.getenv("DISCORD_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24).hex())

DOMAIN = os.getenv("DOMAIN", "https://bot-py-ipa3.onrender.com")
REDIRECT_URI = f"{DOMAIN}/callback"

CONFIG_FILE = "dot_config.json"
OAUTH2_URL = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20guilds"

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            return {}
    return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[ERROR] Failed to save config: {e}")

# ==========================================
# 3. HTML TEMPLATES (ธีม คานูปี้ / KANOPI)
# ==========================================
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>คานูปี้ - Login</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #0f172a; }
        .bg-pink-card { background-color: #fdf2f8; }
        .btn-pink { background-color: #ec4899; }
        .btn-pink:hover { background-color: #db2777; }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl text-center">
        <div class="w-20 h-20 bg-pink-500/10 border border-pink-500/30 rounded-2xl mx-auto flex items-center justify-center mb-6">
            <span class="text-3xl">🌸</span>
        </div>
        <h1 class="text-3xl font-bold text-pink-500 mb-1">Kanopi Login</h1>
        <p class="text-slate-400 text-sm mb-8">เข้าสู่ระบบเพื่อจัดการ Dashboard ของคานูปี้</p>

        <div class="bg-slate-950/60 border border-slate-800 rounded-xl p-4 mb-6 text-left">
            <div class="flex items-center gap-2 text-pink-400 font-semibold text-sm mb-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                ล็อกอินด้วย Discord
            </div>
            <p class="text-xs text-slate-500">ระบบจะพากลับมาหน้าเดิมอัตโนมัติหลังยืนยันตัวตนสำเร็จ</p>
        </div>

        <a href="{{ auth_url }}" class="flex items-center justify-center gap-3 w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 px-6 rounded-xl transition duration-200 shadow-lg shadow-indigo-600/30">
            <svg class="w-5 h-5 fill-current" viewBox="0 0 24 24">
                <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994.021-.041.001-.09-.041-.106a13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.061 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.028zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
            </svg>
            เข้าสู่ระบบด้วย Discord
        </a>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>คานูปี้ - Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #0b0f19; }
    </style>
</head>
<body class="text-slate-100 pb-12">
    <nav class="bg-slate-900/90 border-b border-pink-500/20 px-6 py-4 flex justify-between items-center sticky top-0 z-50 backdrop-blur-md">
        <div class="flex items-center gap-3">
            <span class="text-2xl">🌸</span>
            <span class="text-xl font-bold tracking-wide text-pink-400">คานูปี้ Dashboard</span>
        </div>
        <div class="flex items-center gap-4">
            <div class="flex items-center gap-3 bg-slate-800 border border-slate-700 px-3 py-1.5 rounded-full">
                <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" class="w-7 h-7 rounded-full border border-pink-400">
                <span class="text-sm font-medium text-slate-200">{{ user.username }}</span>
            </div>
            <a href="/logout" class="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 px-4 py-1.5 rounded-lg text-sm transition">ออกจากระบบ</a>
        </div>
    </nav>

    <div class="max-w-4xl mx-auto mt-10 px-4">
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl mb-8 flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold text-white mb-1">ยินดีต้อนรับ, {{ user.username }} 👋</h2>
                <p class="text-slate-400 text-sm">จัดการระบบและตั้งค่าบอทคานูปี้ของคุณได้ที่นี่</p>
            </div>
            <span class="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs px-3 py-1.5 rounded-full">
                <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span> ระบบออนไลน์
            </span>
        </div>

        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl mb-8">
            <div class="flex items-center gap-3 mb-6 border-b border-slate-800 pb-4">
                <div class="w-10 h-10 rounded-lg bg-pink-500/10 border border-pink-500/30 flex items-center justify-center text-pink-400 font-bold">.</div>
                <div>
                    <h3 class="text-lg font-semibold text-white">ตั้งค่าระบบพิมพ์จุดรับยศ (. Verify)</h3>
                    <p class="text-xs text-slate-400">สมาชิกพิมพ์จุด (.) ในช่องที่กำหนดจะได้รับยศทันที</p>
                </div>
            </div>

            <form action="/save_dot_config" method="POST" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-medium text-slate-300 mb-2">Channel ID (ไอดีช่อง):</label>
                        <input type="text" name="channel_id" placeholder="เช่น 123456789012345678" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-pink-500 transition text-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-slate-300 mb-2">Role ID (ไอดีตระกูล/ยศที่จะแจก):</label>
                        <input type="text" name="role_id" placeholder="เช่น 987654321098765432" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-pink-500 transition text-sm">
                    </div>
                </div>
                <button type="submit" class="w-full bg-pink-600 hover:bg-pink-500 text-white font-medium py-2.5 rounded-xl transition duration-200 shadow-md shadow-pink-600/20 text-sm">
                    💾 บันทึกการตั้งค่า
                </button>
            </form>
        </div>

        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h3 class="text-lg font-semibold text-white mb-4">รายการช่องที่เปิดใช้งานในขณะนี้</h3>
            {% if config %}
            <div class="space-y-3">
                {% for ch_id, val in config.items() %}
                <div class="flex items-center justify-between bg-slate-950/60 border border-slate-800 p-4 rounded-xl">
                    <div class="text-sm">
                        <p class="text-pink-400 font-mono"><b>Channel ID:</b> {{ ch_id }}</p>
                        <p class="text-slate-400 font-mono text-xs mt-0.5"><b>Role ID:</b> {{ val.role_id }}</p>
                    </div>
                    <span class="text-xs bg-pink-500/10 text-pink-400 border border-pink-500/20 px-3 py-1 rounded-md">เปิดใช้งานอยู่</span>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="text-center py-8 text-slate-500 text-sm">ยังไม่มีการตั้งค่าระบบพิมพ์จุดในขณะนี้</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# 4. FLASK WEB SERVER (ENHANCED SECURITY)
# ==========================================
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=True
)

@app.route("/")
def index():
    if "user" not in session:
        return render_template_string(LOGIN_HTML, auth_url=OAUTH2_URL)
    
    config = load_config()
    return render_template_string(DASHBOARD_HTML, user=session["user"], config=config)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return redirect(url_for("index"))

    if not CLIENT_SECRET:
        return "Critical Error: CLIENT_SECRET is missing in Environment Variables.", 500

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify guilds"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        token_res = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers, timeout=10)
        token_json = token_res.json()
        access_token = token_json.get("access_token")

        if not access_token:
            return f"Error logging in: {token_json.get('error_description', 'Authentication failed')}", 400

        user_res = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
        session["user"] = user_res.json()
    except requests.RequestException as e:
        return f"Network Error: {str(e)}", 500

    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/save_dot_config", methods=["POST"])
def save_dot_config():
    if "user" not in session:
        return redirect(url_for("index"))

    channel_id = request.form.get("channel_id", "").strip()
    role_id = request.form.get("role_id", "").strip()

    if channel_id.isdigit() and role_id.isdigit():
        config = load_config()
        config[channel_id] = {"role_id": int(role_id)}
        save_config(config)

    return redirect(url_for("index"))

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

threading.Thread(target=run_web, daemon=True).start()

# ==========================================
# 5. DISCORD BOT LOGIC
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ บอทออนไลน์แล้วในชื่อ: {bot.user.name}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    config = load_config()
    channel_id_str = str(message.channel.id)

    if channel_id_str in config:
        if message.content.strip() == ".":
            role_id = config[channel_id_str].get("role_id")
            role = message.guild.get_role(role_id)
            if role:
                try:
                    await message.add_reaction("🌸")
                    await message.author.add_roles(role)
                except Exception as e:
                    print(f"[BOT ERROR] ไม่สามารถแจกยศได้: {e}")

    await bot.process_commands(message)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("[CRITICAL ERROR] DISCORD_TOKEN is missing in Environment Variables!")
    else:
        bot.run(BOT_TOKEN)
