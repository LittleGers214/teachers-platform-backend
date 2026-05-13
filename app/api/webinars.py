from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Webinar, WebinarView

webinars_bp = Blueprint('webinars', __name__)

@webinars_bp.route('/webinars', methods=['GET'])
def list_webinars():
    topic = request.args.get('topic')
    q = request.args.get('q')
    query = Webinar.query.filter_by(is_published=True)
    if topic:
        query = query.filter_by(topic=topic)
    if q:
        query = query.filter(Webinar.title.contains(q))
    webinars = query.all()
    return jsonify([{
        'id': w.id,
        'title': w.title,
        'description': w.description,
        'video_url': w.video_url,
        'topic': w.topic
    } for w in webinars])

@webinars_bp.route('/webinars/<int:id>/view', methods=['POST'])
@jwt_required()
def mark_webinar_viewed(id):
    user_id = int(get_jwt_identity())
    
    existing = WebinarView.query.filter_by(user_id=user_id, webinar_id=id).first()
    if not existing:
        view = WebinarView(user_id=user_id, webinar_id=id)
        db.session.add(view)
        db.session.commit()
    return jsonify({'message': 'Marked as viewed'})