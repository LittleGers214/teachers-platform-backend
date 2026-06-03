from flask import current_app, url_for
from flask_mail import Message
from app.extensions import mail
from itsdangerous import URLSafeTimedSerializer

def send_verification_email(user):
    """Отправляет письмо со ссылкой подтверждения email."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='email-verify')
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    html = f'<p>Добро пожаловать! Для завершения регистрации <a href="{verify_url}">подтвердите email</a>.</p>'
    msg = Message('Подтверждение регистрации',
                  recipients=[user.email],
                  html=html)
    mail.send(msg)
    
    