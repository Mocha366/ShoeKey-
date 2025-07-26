import os, ssl, smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from discord_notify import send_discord_notification

# ───────── 設定読み込み ─────────
load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

# USER_MAP 文字列 → dict へ変換
# 例: "mitti:mail1,kimu:mail2" → {"mitti": "mail1", "kimu": "mail2"}
raw_map = os.getenv("USER_MAP", "")
USER_MAP = {}
if raw_map:
    for item in raw_map.split(","):
        k, v = item.split(":", 1)
        USER_MAP[k.strip()] = v.strip()

# ───────── Flask ─────────
app = Flask(__name__)
CORS(app, resources={r"/trigger": {"origins": "*"}})  # どこからでも許可

def send_mail(subj: str, body: str, to_addr: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"], msg["From"], msg["To"] = subj, GMAIL_USER, to_addr
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(GMAIL_USER, GMAIL_PASS)
        s.send_message(msg)

@app.route("/trigger", methods=["POST"])
def trigger():
    data = request.get_json(force=True)
    raw  = data.get("message", "")          # 例: "Testmitti"
    
    if raw.startswith("Test"):
        user_id = raw[4:]                   # "mitti" 部分を切り出す
        to_addr = USER_MAP.get(user_id)

        if not to_addr:
            return jsonify(error=f"unknown user '{user_id}'"), 400

        try:
            send_mail(
                f"🔓 {user_id} が鍵を開けました！",
                f"MQTT メッセージ: {raw}",
                to_addr
            )
            send_discord_notification(user_id)  # ← ここがDiscord通知！
            return jsonify(status="sent", user=user_id)
        except Exception as e:
            return jsonify(error=str(e)), 500
    return jsonify(status="ignored")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
