import os
import ssl
import smtplib
import threading
import time
import cv2

from email.mime.text import MIMEText
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ───────── 設定読み込み ─────────
load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")  # ← メールに貼る用のホスト名/IP

# USER_MAP の構築
raw_map = os.getenv("USER_MAP", "")
USER_MAP = {}
if raw_map:
    for item in raw_map.split(","):
        k, v = item.split(":", 1)
        USER_MAP[k.strip()] = v.strip()

# ───────── Flask ─────────
app = Flask(__name__)
CORS(app, resources={r"/trigger": {"origins": "*"}})

# カメラ用変数
cap = None
lock = threading.Lock()

def init_camera():
    global cap
    with lock:
        if cap is None:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("カメラが開けませんでした")
                cap = None

def generate_frames():
    global cap
    while True:
        with lock:
            if cap is None:
                break
            ret, frame = cap.read()
        if not ret:
            break
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def send_mail(subj: str, body: str, to_addr: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"], msg["From"], msg["To"] = subj, GMAIL_USER, to_addr
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(GMAIL_USER, GMAIL_PASS)
        s.send_message(msg)

@app.route("/trigger", methods=["POST"])
def trigger():
    data = request.get_json(force=True)
    raw  = data.get("message", "")
    
    if raw.startswith("Test"):
        user_id = raw[4:]
        to_addr = USER_MAP.get(user_id)

        if not to_addr:
            return jsonify(error=f"unknown user '{user_id}'"), 400

        try:
            # メール本文にURLを含める
            url = f"http://{SERVER_HOST}:5000/video_feed"
            body = f"""
🔓 {user_id} が鍵を開けました！

MQTT メッセージ: {raw}
映像はこちらで確認できます: {url}
            """.strip()

            send_mail(
                f"🔔 {user_id} が鍵を開けました！",
                body,
                to_addr
            )

            send_discord_notification(user_id)

            # 10秒後にカメラ起動（非同期）
            threading.Timer(10, init_camera).start()

            return jsonify(status="sent", user=user_id)
        except Exception as e:
            import traceback; traceback.print_exc()   # ← 追加
            return jsonify(error=str(e)), 500

    return jsonify(status="ignored")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
