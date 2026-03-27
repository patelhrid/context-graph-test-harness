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


def _build_payload(user_id: int) -> dict:
        """Build the JWT payload for a given user."""
        return {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
        }


def _encode_token(payload: dict) -> str:
        """Encode a payload dict into a signed JWT string."""
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def generate_token(user_id: int) -> str:
        """Generate a signed JWT token for the given user_id."""
        return _encode_token(_build_payload(user_id))


def verify_token(token: str) -> dict:
        """Decode and verify a JWT token. Raises jwt.ExpiredSignatureError if expired."""
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


@auth_bp.route("/login", methods=["POST"])
def login():
        """Authenticate a user and return a JWT token."""
        data = request.get_json()
        # TODO: validate against DB
        token = generate_token(user_id=data["user_id"])
        return jsonify({"token": token})
