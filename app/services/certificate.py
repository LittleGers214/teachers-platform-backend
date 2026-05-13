from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os
from flask import current_app
from app.models import User, MasterClass
from datetime import datetime

def generate_certificate_pdf(user_id, masterclass_id, score):
    user = User.query.get(user_id)
    mc = MasterClass.query.get(masterclass_id)
    filename = f"cert_{user_id}_{masterclass_id}_{datetime.utcnow().timestamp()}.pdf"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    c.drawString(30, height-50, "СЕРТИФИКАТ")
    c.drawString(30, height-100, f"Настоящим подтверждается, что {user.full_name}")
    c.drawString(30, height-130, f"успешно прошел(а) мастер-класс «{mc.title}»")
    c.drawString(30, height-160, f"с результатом {score}% (проходной балл {mc.passing_score}%)")
    c.drawString(30, height-190, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
    c.drawString(30, height-220, f"Уникальный номер: {user_id}-{masterclass_id}-{int(datetime.now().timestamp())}")
    c.save()
    return filepath