from flask import Flask, jsonify, request, render_template
from datetime import datetime, timedelta
from data_collector import DataCollector
import pandas as pd
app = Flask(__name__)
collector = DataCollector(None)


@app.route("/")
def home():
    collector.create_chart(
        start_time="12-24-2025 00:00:00",
        end_time="12-25-2025 23:59:59",
        frequency="5T",
        smoothing_frequency="1T"
    )
    return render_template("index.html")

@app.route("/api/recent")
def recent():


    df = pd.read_csv("output/output.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    minutes = int(request.args.get("minutes", 15))
    cutoff = df["timestamp"].max() - timedelta(minutes=minutes)

    df = (
        df[df["timestamp"] > cutoff]
        .sort_values("timestamp", ascending=False)
        .head(50)
    )
    return jsonify(df.to_dict(orient="records"))


@app.route("/api/chart-data")
def chart_data():
    frequency = request.args.get("frequency", "5min")
    hours = int(request.args.get("timeframe", 6))
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)

    if hours <= 24:
        smoothing_frequency = "1min"
    elif hours <= 168:      # 1 week
        smoothing_frequency = "5min"
    elif hours <= 720:      # 1 month
        smoothing_frequency  = "1H"
    elif hours <= 2160:     # 3 months
        smoothing_frequency = "1D"
    else:
        smoothing_frequency = "1W"
    collector = DataCollector(None)
    df = collector.create_chart(
        start_time.strftime("%m-%d-%Y %H:%M:%S"),
        end_time.strftime("%m-%d-%Y %H:%M:%S"),
        frequency=frequency,
        smoothing_frequency=smoothing_frequency
    )


    # Convert DataFrame → JSON-friendly format
    if "timestamp" in df.columns:
        timestamps = pd.to_datetime(df["timestamp"], utc=True).dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        ).tolist()
    else:
        timestamps = pd.to_datetime(df.index, utc=True).strftime(
            "%Y-%m-%d %H:%M:%S"
        ).tolist()
    return jsonify({
        "timestamps": timestamps,
        "series": {
            col: df[col].tolist()
            for col in df.columns
            if col != "timestamp"
        }
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

