from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Appeal, UserRole
from app.models import User

appeals_bp = Blueprint('appeals', __name__)

@appeals_bp.route('/appeals', methods=['POST'])
@jwt_required()
def create_appeal():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    appeal = Appeal(
        user_id=user_id,
        full_name=data['full_name'],
        topic=data['topic'],
        message=data['message'],
        # attachment обрабатывается отдельно через multipart
    )
    db.session.add(appeal)
    db.session.commit()
    return jsonify({'message': 'Appeal created'}), 201

@appeals_bp.route('/appeals', methods=['GET'])
@jwt_required()
def get_user_appeals():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if user.role == UserRole.ADMIN:
        appeals = Appeal.query.all()
    else:
        appeals = Appeal.query.filter_by(user_id=user_id)
    return jsonify([{
        'id': a.id,
        'topic': a.topic,
        'message': a.message,
        'status': a.status,
        'admin_comment': a.admin_comment
    } for a in appeals])