"""
Authentication module for Taskly.
Handles login, token generation, and route protection.
Uses JWT tokens for stateless authentication.
"""

import jwt
import datetime
from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)
SECRET_KEY = "dev-secret-key"
TOKEN_EXPIRY_HOURS = 24


def generate_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # TODO: validate against DB
    token = generate_token(user_id=data["user_id"])
    return jsonify({"token": token})
