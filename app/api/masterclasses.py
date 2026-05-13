from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import MasterClass, Test, MasterClassProgress, Certificate
from app.services.certificate import generate_certificate_pdf
from app.services.progress import calculate_score
from datetime import datetime

masterclasses_bp = Blueprint('masterclasses', __name__)

@masterclasses_bp.route('/masterclasses', methods=['GET'])
def list_masterclasses():
    mc = MasterClass.query.filter_by(is_published=True).all()
    return jsonify([{
        'id': m.id,
        'title': m.title,
        'description': m.description,
        'passing_score': m.passing_score
    } for m in mc])

@masterclasses_bp.route('/masterclasses/<int:id>/start', methods=['POST'])
@jwt_required()
def start_masterclass(id):
    user_id = int(get_jwt_identity())
    progress = MasterClassProgress.query.filter_by(user_id=user_id, masterclass_id=id).first()
    if not progress:
        progress = MasterClassProgress(user_id=user_id, masterclass_id=id)
        db.session.add(progress)
        db.session.commit()
    # Получить вопросы тестов
    tests = Test.query.filter_by(masterclass_id=id).all()
    return jsonify({
        'progress_id': progress.id,
        'tests': [{'id': t.id, 'question': t.question_text, 'options': t.options} for t in tests]
    })

@masterclasses_bp.route('/masterclasses/<int:id>/submit', methods=['POST'])
@jwt_required()
def submit_masterclass(id):
    user_id = int(get_jwt_identity())
    data = request.get_json()  # {'answers': {test_id: selected_option_index}}
    progress = MasterClassProgress.query.filter_by(user_id=user_id, masterclass_id=id, completed_at=None).first()
    if not progress:
        return jsonify({'error': 'No active progress'}), 400

    tests = Test.query.filter_by(masterclass_id=id).all()
    score = calculate_score(tests, data['answers'])
    progress.score_percent = score
    progress.answers = data['answers']
    is_passed = score >= (db.session.get(MasterClass, id).passing_score)
    progress.is_passed = is_passed
    if is_passed:
        progress.completed_at = datetime.utcnow()
        # Генерация сертификата
        cert = Certificate.query.filter_by(user_id=user_id, masterclass_id=id).first()
        if not cert:
            cert_pdf = generate_certificate_pdf(user_id, id, score)
            cert = Certificate(
                user_id=user_id,
                masterclass_id=id,
                unique_number=f"MC{id}U{user_id}{datetime.utcnow().timestamp()}",
                pdf_path=cert_pdf
            )
            db.session.add(cert)
            progress.certificate_id = cert.id
    db.session.commit()
    return jsonify({
        'score': score,
        'passed': is_passed,
        'certificate_id': cert.id if is_passed else None
    })