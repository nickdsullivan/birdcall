from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from datetime import timedelta
from get_data import DataCollector

app = Flask(__name__)
CORS(app)

collector = DataCollector(None)

@app.route("/api/recent")
def recent():
    df = pd.read_csv("output/output.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    minutes = int(request.args.get("minutes", 15))
    cutoff = df["timestamp"].max() - timedelta(minutes=minutes)

    df = df[df["timestamp"] > cutoff]
    df = df.sort_values("timestamp", ascending=False).head(50)

    return jsonify(df.to_dict(orient="records"))

@app.route("/api/chart")
def chart():
    start = request.args["start"]
    end = request.args["end"]
    freq = request.args.get("freq", "1H")
    smooth = request.args.get("smooth", "1T")

    df = collector.create_chart(start, end, freq, smooth)

    return jsonify({
        "index": df.index.astype(str).tolist(),
        "data": df.to_dict(orient="list")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
