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
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_query}]
        )

        answer = response.choices[0].message.content
        return jsonify({"response": answer})
    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500

# 🔧 Tell Flask to use Render's dynamic port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
