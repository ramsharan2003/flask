from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import re
from collections import OrderedDict

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/user/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name:
        return jsonify({"message": "Name cannot be left blank", "data": {}}), 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Email is not valid", "data": {}}), 400
    if not password:
        return jsonify({"message": "Password cannot be left blank", "data": {}}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "Email already registered", "data": {}}), 400

    new_user = User(name=name, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)
    return jsonify(OrderedDict([
        ("message", "User signup complete"),
        ("data", {
            "access_token": access_token,
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email
            }
        })
    ])), 200

@user_bp.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"message": "Email is not valid", "data": {}}), 400
    if not password:
        return jsonify({"message": "Password cannot be left blank", "data": {}}), 400

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify(OrderedDict([
            ("message", "Email not registered"),
            ("data", {})
        ])), 404

    if not user.check_password(password):
        return jsonify(OrderedDict([
            ("message", "Invalid password"),
            ("data", {})
        ])), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(OrderedDict([
        ("message", "Login successful"),
        ("data", {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        })
    ])), 200

@user_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_details():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify(OrderedDict([
            ("message", "User detail"),
            ("data", {
                "id": user.id,
                "name": user.name,
                "email": user.email
            })
        ])), 200
    return jsonify(OrderedDict([
        ("message", "User not found"),
        ("data", {})
    ])), 404
