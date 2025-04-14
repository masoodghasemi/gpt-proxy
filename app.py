from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "✅ OpenAI Proxy is Live!"

import traceback  # add this at the top

@app.route("/ask", methods=["POST"])
def ask():
    try:
        query = request.json.get("query", "")
        print("📩 Query received:", query)
        print("🔑 OpenAI Key starts with:", openai.api_key[:5] if openai.api_key else "None")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )

        answer = response.choices[0].message.content
        print("✅ GPT response:", answer)
        return jsonify({"response": answer})

    except Exception as e:
        print("❌ ERROR:", e)
        traceback.print_exc()  # ← this prints full stack trace!
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
