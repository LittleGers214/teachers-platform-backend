from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, MasterClassProgress, Certificate, WebinarView
from werkzeug.security import generate_password_hash
from app.models import User, Certificate, UserRole
import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.extensions import db


profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile/certificates', methods=['GET'])
@jwt_required()
def get_certificates():
    user_id = int(get_jwt_identity())
    certs = Certificate.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': c.id,
        'unique_number': c.unique_number,
        'issue_date': c.issue_date,
        'masterclass_title': c.masterclass.title,
        'pdf_url': f'/api/certificates/{c.id}/download'
    } for c in certs])

@profile_bp.route('/certificates/<int:id>/download', methods=['GET'])
@jwt_required()
def download_certificate(id):
    current_user_id = int(get_jwt_identity())
    cert = Certificate.query.get_or_404(id)
    user = User.query.get(current_user_id)
    is_admin = (user.role == UserRole.ADMIN)

    if cert.user_id != current_user_id and not is_admin:
        return jsonify({'error': 'Access denied'}), 403
    return send_file(cert.pdf_path, as_attachment=True, download_name=f'certificate_{cert.unique_number}.pdf')

@profile_bp.route('/profile/progress', methods=['GET'])
@jwt_required()
def get_progress():
    user_id = int(get_jwt_identity())
    mc_progress = MasterClassProgress.query.filter_by(user_id=user_id).all()
    webinars_viewed = WebinarView.query.filter_by(user_id=user_id).count()
    # Статистика
    return jsonify({
        'masterclasses': [{
            'masterclass_id': p.masterclass_id,
            'title': p.masterclass.title,
            'score': p.score_percent,
            'passed': p.is_passed,
            'completed_at': p.completed_at
        } for p in mc_progress],
        'webinars_viewed': webinars_viewed
    })

@profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
    # или полный URL # avatar_url можно обновить отдельным эндпоинтом загрузки файла
    db.session.commit()
    return jsonify({'message': 'Profile updated'})

@profile_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Создаём папку для аватаров
    avatar_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(avatar_dir, exist_ok=True)

    # Сохраняем файл
    filename = secure_filename(f"user_{user_id}_{file.filename}")
    filepath = os.path.join(avatar_dir, filename)
    file.save(filepath)

    # Удаляем старый аватар, если был
    if user.avatar and os.path.exists(user.avatar):
        os.remove(user.avatar)

    user.avatar = filepath
    db.session.commit()
    return jsonify({'message': 'Avatar uploaded', 'path': filepath}), 200

@profile_bp.route('/avatar', methods=['GET'])
@jwt_required()
def get_avatar():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user.avatar or not os.path.exists(user.avatar):
        return jsonify({'error': 'Avatar not found'}), 404
    return send_file(user.avatar)