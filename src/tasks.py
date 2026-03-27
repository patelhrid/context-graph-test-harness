"""
Task management endpoints.
CRUD operations on Task objects stored in PostgreSQL.
"""

from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError

class TaskCreate(BaseModel):
    title: str
    description: str = ""
from src.models import Task
from src.db import get_db_session

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/", methods=["GET"])
def list_tasks():
    session = get_db_session()
    tasks = session.query(Task).all()
    return jsonify([t.to_dict() for t in tasks])


@tasks_bp.route("/", methods=["POST"])
def create_task():
    data = request.get_json()
    session = get_db_session()
    task = Task(title=data["title"], description=data.get("description", ""))
    session.add(task)
    session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id: int):
    session = get_db_session()
    task = session.query(Task).get(task_id)
    if not task:
        return jsonify({"error": "not found"}), 404
    session.delete(task)
    session.commit()
    return "", 204
