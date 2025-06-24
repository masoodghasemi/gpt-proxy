from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import traceback
import os
import json
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET"])
def home():
    return "✅ GPT Proxy is running."

@app.route("/ask", methods=["POST"])
def ask():
    try:
        body = request.json
        query = body.get("query", "")
        worksheet_data = body.get("worksheet_data", [])

        print("📩 Query:", query)
        print("🧪 Received rows:", len(worksheet_data))

        if not worksheet_data or not isinstance(worksheet_data, list) or not worksheet_data[0]:
            print("⚠️ No data to process.")
            return jsonify({"response": "❌ No valid data received from Tableau."})

        df = pd.DataFrame(worksheet_data)
        print("🧾 Columns detected:", df.columns.tolist())

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

        if numeric_cols and categorical_cols:
            summary_df = df.groupby(categorical_cols)[numeric_cols].sum().reset_index()
        elif numeric_cols:
            summary_df = df[numeric_cols].sum(numeric_only=True).to_frame().T
        else:
            summary_df = df.head(10)

        summary_md = summary_df.to_markdown(index=False)
        print("📊 Summary Table:\n", summary_md)

        system_prompt = (
            "You are a helpful data assistant. The user has provided a summarized table "
            "from a Tableau dashboard. Do not guess missing values or fabricate fields. "
            "Only answer using the information in the table."
        )

        user_prompt = (
            f"{query}\n\nHere is the summarized data:\n\n{summary_md}"
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        answer = response.choices[0].message.content.strip()
        print("✅ GPT Response:", answer or "[EMPTY]")

        return jsonify({"response": answer if answer else "❌ GPT returned no response."})

    except Exception as e:
        print("❌ Exception:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
