import pytest
import uuid
import os
import tempfile
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from app import create_app
from app.config import Config
from app.extensions import db as _db
from app.models import User, UserRole, Webinar, MasterClass, Test

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    JWT_SECRET_KEY = 'test-jwt-secret-key-32-bytes-long!!!'
    # Указываем временную папку для загрузок
    UPLOAD_FOLDER = tempfile.mkdtemp()

# ---------- Основные фикстуры ----------
@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        # Создаём необходимые подпапки
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'certificates'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
        yield app

@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        from app.extensions import db as _db
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# ---------- Очистка базы после каждого теста ----------
@pytest.fixture(autouse=True)
def clean_tables(db):
    yield
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()

@pytest.fixture
def clean_db(clean_tables):
    return clean_tables

# ---------- Фикстуры для пользователей ----------
@pytest.fixture
def create_user(db):
    def _create_user(email, password, full_name, role):
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role=role.value if hasattr(role, 'value') else role
        )
        db.session.add(user)
        db.session.commit()
        return user
    return _create_user

@pytest.fixture
def admin_token(create_user):
    admin = User.query.filter_by(email='admin@test.com').first()
    if not admin:
        admin = create_user(
            email='admin@test.com',
            password='admin123',
            full_name='Admin Test',
            role=UserRole.ADMIN
        )
    return create_access_token(identity=str(admin.id))

@pytest.fixture
def user_token(client, db):
    email = 'user@test.com'
    password = 'password'
    User.query.filter_by(email=email).delete()
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        full_name='Test User',
        role='user'
    )
    db.session.add(user)
    db.session.commit()
    resp = client.post('/api/login', json={'email': email, 'password': password})
    assert resp.status_code == 200
    return resp.json['access_token']

@pytest.fixture
def user(db):
    user = User(
        email='duplicate@example.com',
        password_hash=generate_password_hash('secret'),
        full_name='Duplicate User',
        role='user'
    )
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

# ---------- Фикстуры контента ----------
@pytest.fixture
def webinar(db):
    w = Webinar(title='Test Webinar', video_url='http://test.com', topic='AI')
    db.session.add(w)
    db.session.commit()
    return w

@pytest.fixture
def masterclass(db):
    mc = MasterClass(title='Test MC', passing_score=80, is_published=True)
    db.session.add(mc)
    db.session.commit()

    test1 = Test(
        masterclass_id=mc.id,
        question_text='What is the capital of France?',
        options=[
            {'text': 'Berlin', 'is_correct': False},
            {'text': 'Paris', 'is_correct': True},
            {'text': 'London', 'is_correct': False}
        ]
    )
    test2 = Test(
        masterclass_id=mc.id,
        question_text='What is 2+2?',
        options=[
            {'text': '3', 'is_correct': False},
            {'text': '4', 'is_correct': False},
            {'text': '5', 'is_correct': True}
        ]
    )
    db.session.add_all([test1, test2])
    db.session.commit()
    mc.tests = [test1, test2]
    return mc