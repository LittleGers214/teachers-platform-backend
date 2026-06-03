English
Teachers' Digital Competencies Platform – Backend
Backend for the educational platform aimed at developing digital competencies of teachers, conducting webinars/masterclasses, hosting regulatory documents, surveys, and issuing certificates.

Features
User authentication & roles (guest, registered user, admin)

Normative documents library (PDF, DOCX, links) with search & filters

Webinars & masterclasses with tests, progress tracking, and automatic PDF certificates

Surveys (anonymous/required) with admin analytics

Appeal/consultation requests with status management

Admin panel for content management and user analytics

Certificate generation (PDF, Cyrillic support)

Tech Stack
Python 3.10+

Flask + Flask-RESTful

SQLAlchemy (PostgreSQL / SQLite)

Flask-Migrate (Alembic)

Flask-JWT-Extended

ReportLab (PDF generation)

Pytest for testing

Installation & Setup
Clone the repository:

bash
git clone https://github.com/LittleGers214/teachers-platform-backend.git
cd teachers-platform-backend
Create virtual environment and activate:
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
Install dependencies:
pip install -r requirements.txt

Configure environment variables (create .env file):
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

Run database migrations:
flask db upgrade

Start the development server:
flask run

Running Tests
pytest -v

API Overview
All endpoints are prefixed with /api. See flask routes for full list.
Auth: /register, /login, /profile
Documents: /documents (GET), /documents/<id>/download
Appeals: /appeals (POST, GET)
Webinars: /webinars (GET), /webinars/<id>/view (POST)
Masterclasses: /masterclasses (GET), /masterclasses/<id>/start, /submit
Surveys: /surveys (GET), /surveys/<id>/submit
Profile: /profile/certificates, /profile/progress
Admin: /admin/documents (POST), /admin/masterclasses (POST)
License
MIT
