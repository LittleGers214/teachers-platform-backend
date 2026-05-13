from app.extensions import db
from enum import Enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

class UserRole(str, Enum):
    GUEST = 'guest'      # неавторизованный, в бд не хранится
    USER = 'user'
    ADMIN = 'admin'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default=UserRole.USER)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Связи
    certificates = db.relationship('Certificate', backref='user', lazy=True)
    appeal_messages = db.relationship('Appeal', backref='user', lazy=True)
    masterclass_progress = db.relationship('MasterClassProgress', backref='user', lazy=True)
    survey_responses = db.relationship('SurveyResponse', backref='user', lazy=True)
    webinar_views = db.relationship('WebinarView', backref='user', lazy=True)

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(300))  # путь к PDF/DOCX
    external_link = db.Column(db.String(300))
    category = db.Column(db.String(100))   # например, "закон", "приказ", "методичка"
    tags = db.Column(db.String(200))       # для фильтрации (через запятую)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appeal(db.Model):
    __tablename__ = 'appeals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    attachment_path = db.Column(db.String(300))
    status = db.Column(db.String(50), default='new')  # new, in_progress, completed
    admin_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class Webinar(db.Model):
    __tablename__ = 'webinars'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(300))      # ссылка на видео или путь к файлу
    presentation_path = db.Column(db.String(300))
    materials = db.Column(db.Text)             # доп. материалы (JSON или ссылки)
    topic = db.Column(db.String(100))          # цифровая компетентность, ИИ и т.д.
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WebinarView(db.Model):
    __tablename__ = 'webinar_views'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    webinar_id = db.Column(db.Integer, db.ForeignKey('webinars.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    # для отметки "пройдено" достаточно факта просмотра

class MasterClass(db.Model):
    __tablename__ = 'masterclasses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(300))
    materials = db.Column(db.Text)
    passing_score = db.Column(db.Integer, default=80)   # процент успешного прохождения (0-100)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Связь с тестами
    tests = db.relationship('Test', backref='masterclass', lazy=True, cascade='all, delete-orphan')

class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    masterclass_id = db.Column(db.Integer, db.ForeignKey('masterclasses.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    # варианты ответов в виде JSON: [{"text": "...", "is_correct": false}, ...]
    options = db.Column(db.JSON, nullable=False)
    explanation = db.Column(db.Text)  # пояснение после ответа

class MasterClassProgress(db.Model):
    __tablename__ = 'masterclass_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    masterclass_id = db.Column(db.Integer, db.ForeignKey('masterclasses.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    score_percent = db.Column(db.Float)          # набранный процент
    is_passed = db.Column(db.Boolean, default=False)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=True)
    
    answers = db.Column(db.JSON)  # {test_id: selected_option_index}
    masterclass = db.relationship('MasterClass', backref='progresses')

class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    masterclass_id = db.Column(db.Integer, db.ForeignKey('masterclasses.id'), nullable=False)
    unique_number = db.Column(db.String(50), unique=True, nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    pdf_path = db.Column(db.String(300), nullable=False)  # путь к сгенерированному PDF

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    topic = db.Column(db.String(100))  # цифровая компетентность, ИИ и т.д.
    is_required = db.Column(db.Boolean, default=True)  # обязательно для всех пользователей
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('SurveyQuestion', backref='survey', lazy=True, cascade='all, delete-orphan')

class SurveyQuestion(db.Model):
    __tablename__ = 'survey_questions'
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='radio')  # radio, checkbox, text
    options = db.Column(db.JSON)  # для radio/checkbox список вариантов

class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    answers = db.Column(db.JSON)  # {question_id: answer_value}
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)