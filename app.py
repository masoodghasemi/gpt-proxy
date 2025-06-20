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
    return "✅ GPT Proxy is running."

@app.route("/ask", methods=["POST"])
def ask():
    try:
        body = request.json
        query = body.get("query", "")
        worksheet_data = body.get("worksheet_data", [])
        columns = body.get("columns", [])

        system_prompt = (
            "You are a helpful data assistant. The user has provided worksheet data from a Tableau dashboard. "
            "Interpret the structure yourself and answer their question accurately using only the data provided. "
            "Group, filter, or summarize based on the user prompt, but do not assume field meanings unless evident."
        )

        user_message = f"{query}\n\nData sample:\n" + json.dumps(worksheet_data, indent=2)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        return jsonify({"response": response.choices[0].message.content.strip()})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
