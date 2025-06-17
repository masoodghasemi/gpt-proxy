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

        # Generic system prompt
        system_prompt = (
            "You are a helpful assistant analyzing structured data from a Tableau dashboard. "
            "You may receive a list of data rows with various columns, including numeric and categorical values. "
            "Respond to questions using only the data provided. Group, filter, or summarize as needed, "
            "but do not guess or hallucinate values."
        )

        # Format the user message
        user_message = f"{query}\n\nHere is the worksheet data (first 10 rows):\n" + json.dumps(worksheet_data[:10], indent=2)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({"response": answer})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
