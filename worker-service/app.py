from flask import Flask, jsonify
import boto3, os
from datetime import datetime

app = Flask(__name__)
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("tasks")

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/process")
def process():
    # Scan for pending tasks older than 1 day — mark as overdue
    resp = table.scan(
        FilterExpression="status = :s",
        ExpressionAttributeValues={":s": "pending"}
    )
    updated = 0
    for item in resp["Items"]:
        created = datetime.fromisoformat(item["created_at"])
        if (datetime.utcnow() - created).days >= 1:
            table.update_item(
                Key={"user_id": item["user_id"], "task_id": item["task_id"]},
                UpdateExpression="SET #s = :overdue",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":overdue": "overdue"}
            )
            updated += 1
    return jsonify({"processed": updated})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)