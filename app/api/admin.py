import os
from werkzeug.utils import secure_filename
from flask import current_app
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, UserRole, Document, MasterClass
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, ) 

def admin_required(f):
    from functools import wraps
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if not user or user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin required'}), 403
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/documents', methods=['POST'])
@admin_required
def upload_document():
    data = request.form
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    doc = Document(
        title=title,
        description=data.get('description', ''),
        category=data.get('category', '')
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify({'id': doc.id}), 201

@admin_bp.route('/masterclasses', methods=['POST'])
@admin_required
def create_masterclass():
    data = request.get_json()
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    mc = MasterClass(
        title=title,
        description=data.get('description', ''),
        passing_score=data.get('passing_score', 80)
    )
    db.session.add(mc)
    db.session.commit()
    return jsonify({'id': mc.id}), 201