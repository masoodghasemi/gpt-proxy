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

@app.route("/ask", methods=["POST"])
def ask():
    try:
        query = request.json.get("query", "")
        print("📩 Incoming query:", query)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or gpt-4o if your key supports it
            messages=[{"role": "user", "content": query}]
        )

        answer = response.choices[0].message.content
        return jsonify({"response": answer})

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
