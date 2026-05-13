import os
from datetime import datetime
from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.models import User, MasterClass


FONT_PATH = "C:/Windows/Fonts/arial.ttf"  


try:
    pdfmetrics.registerFont(TTFont('Arial', FONT_PATH))
except:
    
    print("Warning: Arial not found, cyrillic may not render correctly.")
    pdfmetrics.registerFont(TTFont('Arial', 'Helvetica'))  # fallback

def generate_certificate_pdf(user_id, masterclass_id, score):
    user = User.query.get(user_id)
    mc = MasterClass.query.get(masterclass_id)
    filename = f"cert_{user_id}_{masterclass_id}_{datetime.utcnow().timestamp()}.pdf"
    cert_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
    os.makedirs(cert_dir, exist_ok=True)
    filepath = os.path.join(cert_dir, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    
    c.setFont('Arial', 16)

   
    c.drawString(100, height - 100, "СЕРТИФИКАТ")
    c.setFont('Arial', 12)
    c.drawString(100, height - 140, f"Настоящим подтверждается, что {user.full_name}")
    c.drawString(100, height - 170, f"успешно прошел(а) мастер-класс «{mc.title}»")
    c.drawString(100, height - 200, f"с результатом {score:.1f}% (проходной балл {mc.passing_score}%)")
    c.drawString(100, height - 240, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")
    c.drawString(100, height - 270, f"Уникальный номер: {user.id}-{mc.id}-{int(datetime.now().timestamp())}")

    c.save()
    
    return filepath