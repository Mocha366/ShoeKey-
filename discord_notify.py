import os
import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_sender_name(msg):
    mapping = {
        "mitti": "みっちーが帰ってきたよ！",
        "kimu": "きむらのおでましぃ！",
        "pote": "ポテコ様が帰宅なされたぞ！",
        "tomato": "hatomatoがLOLをしに帰宅しました!"
    }
    return mapping.get(msg, f"誰かが来たよ！（{msg}）")

def send_discord_notification(msg):
    text = get_sender_name(msg)
    payload = { "content": f"🔔 {text}" }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        print(f"Discord通知ステータス: {response.status_code}")
    except Exception as e:
        print(f"Discord通知エラー: {e}")
