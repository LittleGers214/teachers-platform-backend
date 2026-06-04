from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, MasterClassProgress, Certificate, WebinarView
from werkzeug.security import generate_password_hash
from app.models import User, Certificateertificate, UserRole
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
    # avatar_url можно обновить отдельным эндпоинтом загрузки файла
    db.session.commit()
    return jsonify({'message': 'Profile updated'})

# Загрузка аватарки для текущего пользователя
@profile_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    filename = secure_filename(f"{get_jwt_identity()}_{file.filename}")
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    avatar_url = f"/uploads/avatars/{filename}"
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    user.avatar_url = avatar_url
    db.session.commit()
    return jsonify({'avatar_url': avatar_url}), 200