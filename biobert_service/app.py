from flask import Flask, request, jsonify
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os

app = Flask(__name__)

tokenizer = BertTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
model = BertForSequenceClassification.from_pretrained(
    "dmis-lab/biobert-base-cased-v1.1",
    num_labels=7
)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("message", "")

    if not text:
        return jsonify({"intent": "UNKNOWN"})

    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model(**inputs)
    intent_id = torch.argmax(outputs.logits, dim=1).item()

    intents = [
        "GET_BLOOD_GROUP",
        "GET_ALLERGIES",
        "GET_MEDICATIONS",
        "GET_PROFILE_SUMMARY",
        "GET_LATEST_REPORT",
        "GET_REPORT_LIST",
        "UNKNOWN"
    ]

    return jsonify({"intent": intents[intent_id]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
