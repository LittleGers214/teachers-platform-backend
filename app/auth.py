from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, UserRole
from app.utils.email import send_verification_email
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, request, jsonify, url_for
from flask_mail import Message
from app.extensions import mail

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    hashed = generate_password_hash(data['password'])
    user = User(
        email=data['email'],
        password_hash=hashed,
        full_name=data['full_name'],
        role=UserRole.USER
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    hashed = generate_password_hash(data['password'])
    user = User(
        email=data['email'],
        password_hash=hashed,
        full_name=data['full_name'],
        is_verified=False
    )
    db.session.add(user)
    db.session.commit()
    # Отправляем письмо (в фоне или синхронно)
    try:
        send_verification_email(user)
    except Exception as e:
        # Логируем ошибку, но пользователя не откатываем
        print(f"Email sending failed: {e}")
    return jsonify({'message': 'User created. Check your email for verification.'}), 201

@auth_bp.route('/verify-email', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verify', max_age=86400)  # 24 часа
    except Exception:
        return jsonify({'error': 'Invalid or expired token'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user.is_verified:
        return jsonify({'message': 'Email already verified'}), 200
    user.is_verified = True
    db.session.commit()
    return jsonify({'message': 'Email verified successfully'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token, 'role': user.role})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role         
    })
