from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt, ma
from app.auth import auth_bp
from app.api.documents import documents_bp
from app.api.appeals import appeals_bp
from app.api.webinars import webinars_bp
from app.api.masterclasses import masterclasses_bp
from app.api.surveys import surveys_bp
from app.api.profile import profile_bp
from app.models import User, Document, Appeal, Webinar, WebinarView,  MasterClass, Test, MasterClassProgress, Certificate, Survey, SurveyQuestion, SurveyResponse
from app.api.admin import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(documents_bp, url_prefix='/api')
    app.register_blueprint(appeals_bp, url_prefix='/api')
    app.register_blueprint(webinars_bp, url_prefix='/api')
    app.register_blueprint(masterclasses_bp, url_prefix='/api')
    app.register_blueprint(surveys_bp, url_prefix='/api')
    app.register_blueprint(profile_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    return app