from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Survey, SurveyResponse

surveys_bp = Blueprint('surveys', __name__)

@surveys_bp.route('/surveys', methods=['GET'])
@jwt_required()
def list_surveys():
    user_id = int(get_jwt_identity())
    # Получить все активные анкеты
    surveys = Survey.query.filter_by(is_active=True).all()
    result = []
    for s in surveys:
        # проверить, проходил ли пользователь
        responded = SurveyResponse.query.filter_by(user_id=user_id, survey_id=s.id).first()
        result.append({
            'id': s.id,
            'title': s.title,
            'description': s.description,
            'is_completed': responded is not None
        })
    return jsonify(result)

@surveys_bp.route('/surveys/<int:id>', methods=['GET'])
@jwt_required()
def get_survey(id):
    survey = Survey.query.get_or_404(id)
    return jsonify({
        'id': survey.id,
        'title': survey.title,
        'questions': [{'id': q.id, 'text': q.question_text, 'type': q.question_type, 'options': q.options} for q in survey.questions]
    })

@surveys_bp.route('/surveys/<int:id>/submit', methods=['POST'])
@jwt_required()
def submit_survey(id):
    user_id = int(get_jwt_identity())
    data = request.get_json()  # {'answers': {question_id: value}}
    # Проверить, не отвечал ли уже
    existing = SurveyResponse.query.filter_by(user_id=user_id, survey_id=id).first()
    if existing:
        return jsonify({'error': 'Already responded'}), 400
    response = SurveyResponse(user_id=user_id, survey_id=id, answers=data['answers'])
    db.session.add(response)
    db.session.commit()
    return jsonify({'message': 'Submitted'})