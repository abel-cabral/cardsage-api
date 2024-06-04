import datetime

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from ..shared import collection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/user/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    mongodb = collection('users')
    user = mongodb.find_one({"email": email})
    if user:
        return jsonify({"msg": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    mongodb.insert_one({"email": email, "password": hashed_password})
    
    return jsonify({"msg": "User registered successfully"}), 201

@auth_bp.route('/api/user/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400

    mongodb = collection('users')
    user = mongodb.find_one({"email": email})
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401

    # Debugging: Verifique se o usuário e a senha estão corretos
    if check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401

@auth_bp.route('/api/user/logout', methods=['POST'])
@jwt_required()
def logout():
    mongodb = collection('revoked_tokens')
    jti = get_jwt()["jti"]
    mongodb.insert_one({"jti": jti})
    return jsonify({"msg": "Successfully logged out"}), 200

__all__ = ['register', 'login', 'logout']