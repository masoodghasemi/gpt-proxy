from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import traceback
import json

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "✅ OpenAI Proxy is Live!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        body = request.json
        query = body.get("query", "")
        worksheet_data = body.get("worksheet_data", [])
        columns = body.get("columns", [])

        print("📩 Query received:", query)
        print("📊 Received data rows:", len(worksheet_data))
        print("🧠 First row sample:", worksheet_data[0] if worksheet_data else "None")

        # System prompt to guide GPT
        system_prompt = (
            "You are a helpful assistant for analyzing Tableau worksheet data. "
            "You will be given structured data in JSON format. "
            "If the user asks for statistics, you should compute count, average, min, and max "
            "for any numeric columns you detect. Respond clearly and concisely."
        )

        # Compose the user prompt
        user_message = query
        if worksheet_data:
            sample_rows = worksheet_data[:10]  # send only top rows to stay under token limit
            user_message += f"\n\nHere is worksheet data:\n{json.dumps(sample_rows, indent=2)}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        answer = response.choices[0].message.content.strip()
        print("✅ GPT response:", answer)
        return jsonify({"response": answer})

    except Exception as e:
        print("❌ ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
