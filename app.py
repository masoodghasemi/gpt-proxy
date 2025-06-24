from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import traceback
import os
import json
import openai

app = Flask(__name__)
CORS(app)

# Use default OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "✅ GPT Proxy is running."

@app.route("/ask", methods=["POST"])
def ask():
    try:
        body = request.json
        query = body.get("query", "").strip()
        worksheet_data = body.get("worksheet_data", [])

        print("📩 Query:", query)
        print("🧪 Rows received:", len(worksheet_data))

        if not worksheet_data or not isinstance(worksheet_data, list) or not worksheet_data[0]:
            return jsonify({"response": "❌ No valid data received from Tableau."})

        # Convert to DataFrame
        df = pd.DataFrame(worksheet_data)
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

        # Summarize or fallback
        if numeric_cols and categorical_cols:
            summary_df = df.groupby(categorical_cols)[numeric_cols].sum().reset_index()
        elif numeric_cols:
            summary_df = df[numeric_cols].sum(numeric_only=True).to_frame().T
        else:
            summary_df = df.head(10)

        summary_text = summary_df.to_csv(index=False)
        print("📊 Summary CSV:\n", summary_text)

        # Construct system + user prompt
        system_prompt = (
            "You are a helpful assistant working with structured data from a Tableau dashboard. "
            "You are given a CSV summary table and a user question. "
            "Answer only based on the table. Do not invent data or make assumptions."
        )

        user_prompt = f"{query}\n\nHere is the summarized data:\n\n{summary_text}"

        print("🧠 Final prompt to GPT:\n", user_prompt)

        # Call GPT (OpenAI SDK v1)
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        answer = response.choices[0].message.content.strip()
        if not answer:
            answer = "❌ GPT returned an empty response. Please try again or rephrase your question."
        print("✅ GPT response:\n", answer)

        return jsonify({"response": answer})

    except Exception as e:
        print("❌ Exception occurred:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
