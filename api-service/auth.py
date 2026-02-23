import os, requests
from functools import wraps
from flask import request, jsonify
from jose import jwt, JWTError

REGION = "us-east-1"
USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

def get_public_keys():
    return requests.get(JWKS_URL).json()["keys"]

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "No token provided"}), 401
        try:
            keys = get_public_keys()
            claims = jwt.decode(token, keys, algorithms=["RS256"],
                                audience=CLIENT_ID)
            user_id = claims["sub"]
            return f(user_id, *args, **kwargs)
        except JWTError as e:
            return jsonify({"error": "Invalid token"}), 401
    return decorated