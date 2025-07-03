from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import traceback
import os
from openai import OpenAI  # ✅ CORRECT import

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

        df = pd.DataFrame(worksheet_data)
        print("🧾 Raw DataFrame from Tableau:")
        print(df.head(50).to_string(index=False))

        # Keep only a few rows if too large (optional safety net)
        if len(df) > 500:
            df = df.head(500)
            
        summary_text = df.to_markdown(index=False)
        #print("📊 Data Markdown:\n", summary_text)

        system_prompt = (
            "You are a helpful assistant analyzing structured data from a Tableau dashboard. "
            "Only use the data provided below to answer the question. Do not guess or fabricate values. "
            "Apply any filtering, summarization or logic directly on the data."
        )

        user_prompt = f"{query}\n\nHere is the data:\n\n{summary_text}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        answer = response.choices[0].message.content.strip()
        if not answer:
            answer = "❌ GPT returned an empty response."
        print("✅ GPT response:\n", answer)

        return jsonify({"response": answer})

    except Exception as e:
        print("❌ Exception occurred:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
