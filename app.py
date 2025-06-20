from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import traceback
import json
import pandas as pd

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

        if not worksheet_data or not isinstance(worksheet_data, list):
            return jsonify({"error": "Invalid worksheet data."}), 400

        df = pd.DataFrame(worksheet_data)

        # Identify types
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

        # Group + summarize
        if numeric_cols and categorical_cols:
            summary_df = df.groupby(categorical_cols)[numeric_cols].sum().reset_index()
        elif numeric_cols:
            summary_df = df[numeric_cols].sum(numeric_only=True).to_frame().T
        else:
            summary_df = df.head(10)  # fallback if no numeric fields

        summary_markdown = summary_df.to_markdown(index=False)

        # Construct GPT prompt
        system_prompt = (
            "You are a data assistant. The user has provided a summarized table of worksheet data. "
            "Answer the question using only the table. Do not make up numbers or columns."
        )

        user_prompt = (
            f"{query}\n\n"
            "Here is the summarized data:\n\n"
            f"{summary_markdown}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return jsonify({"response": response.choices[0].message.content.strip()})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
