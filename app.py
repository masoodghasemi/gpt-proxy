from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "✅ GPT Proxy is Live!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_query = request.json.get("query", "")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or gpt-4o if your key supports it
            messages=[
                {"role": "user", "content": user_query}
            ]
        )

        answer = response.choices[0].message.content
        return jsonify({"response": answer})
    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500
