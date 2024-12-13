from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os
from dotenv import load_dotenv

# โหลดค่า ENV
load_dotenv()

# LINE API Configuration
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # ส่งข้อความไปยัง OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    reply_message = response["choices"][0]["message"]["content"].strip()

    # ส่งข้อความกลับผู้ใช้
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
