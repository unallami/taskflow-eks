from flask import Flask, request, jsonify
import boto3, uuid, os
from datetime import datetime
from auth import require_auth

app = Flask(__name__)
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("tasks")

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/tasks", methods=["GET"])
@require_auth
def get_tasks(user_id):
    resp = table.query(
        KeyConditionExpression="user_id = :uid",
        ExpressionAttributeValues={":uid": user_id}
    )
    return jsonify(resp["Items"])

@app.route("/tasks", methods=["POST"])
@require_auth
def create_task(user_id):
    data = request.json
    task = {
        "user_id": user_id,
        "task_id": str(uuid.uuid4()),
        "title": data["title"],
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    table.put_item(Item=task)
    return jsonify(task), 201

@app.route("/tasks/<task_id>", methods=["DELETE"])
@require_auth
def delete_task(user_id, task_id):
    table.delete_item(
        Key={"user_id": user_id, "task_id": task_id}
    )
    return jsonify({"deleted": task_id})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)