import os
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import User, UserRole
from app.models import Document as DocumentModel  # переименовали, чтобы не конфликтовать с docx
from app.models import Webinar, MasterClass, Test, Survey, SurveyQuestion, WebinarView
from docx import Document as DocxDocument  # импорт docx с псевдонимом
from app.utils.parser import parse_question_file
from app.models import Certificate, MasterClassProgress
from app.models import Document as DocumentModel

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if not user or user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin required'}), 403
        return f(*args, **kwargs)
    return decorated

# ========== Управление документами ==========
@admin_bp.route('/documents', methods=['GET'])
@admin_required
def list_all_documents():
    docs = DocumentModel.query.all()
    return jsonify([{
        'id': d.id,
        'title': d.title,
        'description': d.description,
        'category': d.category,
        'file_path': d.file_path,
        'external_link': d.external_link,
        'uploaded_at': d.uploaded_at.isoformat() if d.uploaded_at else None,
    } for d in docs])

@admin_bp.route('/documents', methods=['POST'])
@admin_required
def create_document():
    data = request.form
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Title required'}), 400
    file = request.files.get('file')
    file_path = None
    if file:
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
    doc = DocumentModel(
        title=title,
        description=data.get('description', ''),
        category=data.get('category', ''),
        file_path=file_path,
        external_link=data.get('external_link')
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify({'id': doc.id}), 201

@admin_bp.route('/documents/<int:doc_id>', methods=['PUT'])
@admin_required
def update_document(doc_id):
    doc = DocumentModel.query.get_or_404(doc_id)
    data = request.get_json()
    doc.title = data.get('title', doc.title)
    doc.description = data.get('description', doc.description)
    doc.category = data.get('category', doc.category)
    doc.external_link = data.get('external_link', doc.external_link)
    db.session.commit()
    return jsonify({'message': 'Document updated'}), 200

@admin_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
@admin_required
def delete_document(doc_id):
    doc = DocumentModel.query.get_or_404(doc_id)
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.session.delete(doc)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# ========== Управление вебинарами ==========
@admin_bp.route('/webinars', methods=['GET'])
@admin_required
def list_webinars_admin():
    webinars = Webinar.query.all()
    return jsonify([{
        'id': w.id,
        'title': w.title,
        'description': w.description,
        'video_url': w.video_url,
        'presentation_path': w.presentation_path,
        'materials': w.materials,
        'topic': w.topic,
        'is_published': w.is_published,
    } for w in webinars])

@admin_bp.route('/webinars', methods=['POST'])
@admin_required
def create_webinar():
    if request.is_json:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        video_url = data.get('video_url')
        presentation_path = data.get('presentation_path')
        materials = data.get('materials')
        topic = data.get('topic')
        is_published = data.get('is_published', True)
        video_file = None
    else:
        title = request.form.get('title')
        description = request.form.get('description', '')
        video_url = request.form.get('video_url')
        presentation_path = request.form.get('presentation_path')
        materials = request.form.get('materials')
        topic = request.form.get('topic')
        is_published = request.form.get('is_published', 'true').lower() == 'true'
        video_file = request.files.get('video')

    if not title:
        return jsonify({'error': 'Title required'}), 400

    saved_video_path = None
    if video_file and video_file.filename:
        filename = secure_filename(video_file.filename)
        video_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
        os.makedirs(video_dir, exist_ok=True)
        saved_video_path = os.path.join(video_dir, filename).replace('\\', '/')
        video_file.save(saved_video_path)

    final_video_url = saved_video_path or video_url

    webinar = Webinar(
        title=title,
        description=description,
        video_url=final_video_url,
        presentation_path=presentation_path,
        materials=materials,
        topic=topic,
        is_published=is_published
    )
    db.session.add(webinar)
    db.session.commit()
    return jsonify({'id': webinar.id}), 201

@admin_bp.route('/webinars/<int:webinar_id>', methods=['PUT'])
@admin_required
def update_webinar(webinar_id):
    webinar = Webinar.query.get_or_404(webinar_id)
    if request.is_json:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        video_url = data.get('video_url')
        presentation_path = data.get('presentation_path')
        materials = data.get('materials')
        topic = data.get('topic')
        is_published = data.get('is_published')
        video_file = None
    else:
        title = request.form.get('title')
        description = request.form.get('description')
        video_url = request.form.get('video_url')
        presentation_path = request.form.get('presentation_path')
        materials = request.form.get('materials')
        topic = request.form.get('topic')
        is_published = request.form.get('is_published')
        video_file = request.files.get('video')

    if title is not None:
        webinar.title = title
    if description is not None:
        webinar.description = description
    if presentation_path is not None:
        webinar.presentation_path = presentation_path
    if materials is not None:
        webinar.materials = materials
    if topic is not None:
        webinar.topic = topic
    if is_published is not None:
        webinar.is_published = is_published

    if video_file and video_file.filename:
        old_path = webinar.video_url
        if old_path and os.path.exists(old_path):
            os.remove(old_path)
        filename = secure_filename(video_file.filename)
        video_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
        os.makedirs(video_dir, exist_ok=True)
        new_path = os.path.join(video_dir, filename).replace('\\', '/')
        video_file.save(new_path)
        webinar.video_url = new_path
    elif video_url is not None:
        webinar.video_url = video_url

    db.session.commit()
    return jsonify({'message': 'Webinar updated'}), 200

@admin_bp.route('/webinars/<int:webinar_id>', methods=['DELETE'])
@admin_required
def delete_webinar(webinar_id):
    webinar = Webinar.query.get_or_404(webinar_id)
    if webinar.video_url and os.path.exists(webinar.video_url):
        os.remove(webinar.video_url)
    db.session.delete(webinar)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# ========== Управление мастер-классами ==========
@admin_bp.route('/masterclasses', methods=['GET'])
@admin_required
def list_masterclasses_admin():
    mcs = MasterClass.query.all()
    return jsonify([{
        'id': m.id,
        'title': m.title,
        'description': m.description,
        'passing_score': m.passing_score,
        'is_published': m.is_published,
        'video_url': m.video_url,
        'materials': m.materials,
    } for m in mcs])

@admin_bp.route('/masterclasses', methods=['POST'])
@admin_required
def create_masterclass():
    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'Title required'}), 400
    mc = MasterClass(
        title=data['title'],
        description=data.get('description', ''),
        passing_score=data.get('passing_score', 80),
        is_published=data.get('is_published', True),
        video_url=data.get('video_url'),
        materials=data.get('materials')
    )
    db.session.add(mc)
    db.session.commit()
    return jsonify({'id': mc.id}), 201

@admin_bp.route('/masterclasses/<int:mc_id>', methods=['PUT'])
@admin_required
def update_masterclass(mc_id):
    mc = MasterClass.query.get_or_404(mc_id)
    data = request.get_json()
    mc.title = data.get('title', mc.title)
    mc.description = data.get('description', mc.description)
    mc.passing_score = data.get('passing_score', mc.passing_score)
    mc.is_published = data.get('is_published', mc.is_published)
    mc.video_url = data.get('video_url', mc.video_url)
    mc.materials = data.get('materials', mc.materials)
    db.session.commit()
    return jsonify({'message': 'Masterclass updated'}), 200

@admin_bp.route('/masterclasses/<int:mc_id>', methods=['DELETE'])
@admin_required
def delete_masterclass(mc_id):
    mc = MasterClass.query.get_or_404(mc_id)
    Certificate.query.filter_by(masterclass_id=mc_id).delete()
    MasterClassProgress.query.filter_by(masterclass_id=mc_id).delete()
    Test.query.filter_by(masterclass_id=mc_id).delete()
    db.session.delete(mc)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# ========== Управление тестами (вопросами мастер-классов) ==========
@admin_bp.route('/masterclasses/<int:mc_id>/tests', methods=['GET'])
@admin_required
def get_tests(mc_id):
    tests = Test.query.filter_by(masterclass_id=mc_id).all()
    return jsonify([{
        'id': t.id,
        'question_text': t.question_text,
        'options': t.options,
        'explanation': t.explanation
    } for t in tests])

@admin_bp.route('/masterclasses/<int:mc_id>/tests', methods=['POST'])
@admin_required
def add_test(mc_id):
    data = request.get_json()
    mc = MasterClass.query.get_or_404(mc_id)
    test = Test(
        masterclass_id=mc.id,
        question_text=data['question_text'],
        options=data['options'],
        explanation=data.get('explanation')
    )
    db.session.add(test)
    db.session.commit()
    return jsonify({'id': test.id}), 201

@admin_bp.route('/tests/<int:test_id>', methods=['GET'])
@admin_required
def get_test(test_id):
    test = Test.query.get_or_404(test_id)
    return jsonify({
        'id': test.id,
        'question_text': test.question_text,
        'options': test.options,
        'explanation': test.explanation,
        'masterclass_id': test.masterclass_id
    })

@admin_bp.route('/tests/<int:test_id>', methods=['PUT'])
@admin_required
def update_test(test_id):
    test = Test.query.get_or_404(test_id)
    data = request.get_json()
    test.question_text = data.get('question_text', test.question_text)
    test.options = data.get('options', test.options)
    test.explanation = data.get('explanation', test.explanation)
    db.session.commit()
    return jsonify({'message': 'Test updated'}), 200

@admin_bp.route('/tests/<int:test_id>', methods=['DELETE'])
@admin_required
def delete_test(test_id):
    test = Test.query.get_or_404(test_id)
    db.session.delete(test)
    db.session.commit()
    return jsonify({'message': 'Test deleted'}), 200

# ========== Управление анкетами ==========
@admin_bp.route('/surveys', methods=['GET'])
@admin_required
def list_surveys_admin():
    surveys = Survey.query.all()
    return jsonify([{
        'id': s.id,
        'title': s.title,
        'description': s.description,
        'topic': s.topic,
        'is_required': s.is_required,
        'is_active': s.is_active,
    } for s in surveys])

@admin_bp.route('/surveys', methods=['POST'])
@admin_required
def create_survey():
    data = request.get_json()
    if not data.get('title'):
        return jsonify({'error': 'Title required'}), 400
    survey = Survey(
        title=data['title'],
        description=data.get('description', ''),
        topic=data.get('topic'),
        is_required=data.get('is_required', True),
        is_active=data.get('is_active', True)
    )
    db.session.add(survey)
    db.session.commit()
    return jsonify({'id': survey.id}), 201

@admin_bp.route('/surveys/<int:survey_id>', methods=['PUT'])
@admin_required
def update_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    data = request.get_json()
    survey.title = data.get('title', survey.title)
    survey.description = data.get('description', survey.description)
    survey.topic = data.get('topic', survey.topic)
    survey.is_required = data.get('is_required', survey.is_required)
    survey.is_active = data.get('is_active', survey.is_active)
    db.session.commit()
    return jsonify({'message': 'Survey updated'}), 200

@admin_bp.route('/surveys/<int:survey_id>', methods=['DELETE'])
@admin_required
def delete_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    db.session.delete(survey)
    db.session.commit()
    return jsonify({'message': 'Deleted'}), 200

# ========== Управление вопросами анкет ==========
@admin_bp.route('/surveys/<int:survey_id>/questions', methods=['POST'])
@admin_required
def add_question(survey_id):
    data = request.get_json()
    survey = Survey.query.get_or_404(survey_id)
    question = SurveyQuestion(
        survey_id=survey.id,
        question_text=data['question_text'],
        question_type=data.get('question_type', 'radio'),
        options=data.get('options')
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({'id': question.id}), 201

@admin_bp.route('/survey-questions/<int:question_id>', methods=['PUT'])
@admin_required
def update_question(question_id):
    question = SurveyQuestion.query.get_or_404(question_id)
    data = request.get_json()
    question.question_text = data.get('question_text', question.question_text)
    question.question_type = data.get('question_type', question.question_type)
    question.options = data.get('options', question.options)
    db.session.commit()
    return jsonify({'message': 'Question updated'}), 200

@admin_bp.route('/survey-questions/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_question(question_id):
    question = SurveyQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted'}), 200

# ========== Управление пользователями ==========
@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'email': u.email,
        'full_name': u.full_name,
        'role': u.role.value if hasattr(u.role, 'value') else u.role,
        'is_active': u.is_active,
        'created_at': u.created_at.isoformat() if u.created_at else None,
    } for u in users])

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if 'role' in data:
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'full_name' in data:
        user.full_name = data['full_name']
    db.session.commit()
    return jsonify({'message': 'User updated'}), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

# ========== Загрузка файлов и парсер вопросов ==========
@admin_bp.route('/upload', methods=['POST'])
@admin_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    file_url = f"/uploads/{filename}"
    return jsonify({'url': file_url}), 201

@admin_bp.route('/masterclasses/<int:masterclass_id>/upload-questions', methods=['POST'])
@admin_required
def upload_questions(masterclass_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ['txt', 'docx']:
        return jsonify({'error': 'Only .txt or .docx files are supported'}), 400

    try:
        if ext == 'txt':
            content = file.read().decode('utf-8')
        else:  # docx
            doc = DocxDocument(file)  # используем DocxDocument
            content = '\n'.join([p.text for p in doc.paragraphs])
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 400

    tests_data = parse_question_file(content)
    if not tests_data:
        return jsonify({'error': 'No questions found in file'}), 400

    masterclass = MasterClass.query.get(masterclass_id)
    if not masterclass:
        return jsonify({'error': 'Masterclass not found'}), 404

    new_tests = []
    for data in tests_data:
        test = Test(
            masterclass_id=masterclass_id,
            question_text=data['question_text'],
            options=data['options'],
            explanation=None
        )
        new_tests.append(test)

    db.session.add_all(new_tests)
    db.session.commit()
    return jsonify({'message': f'Added {len(new_tests)} tests', 'tests': tests_data}), 201