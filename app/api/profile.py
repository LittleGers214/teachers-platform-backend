from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, MasterClassProgress, Certificate, WebinarView

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
    user_id = int(get_jwt_identity())
    cert = Certificate.query.get_or_404(id)
    if cert.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    return send_file(cert.pdf_path, as_attachment=True)

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