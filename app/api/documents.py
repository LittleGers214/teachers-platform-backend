from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Document, UserRole
from app.schemas import DocumentSchema
import os
from werkzeug.utils import secure_filename

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/documents', methods=['GET'])
def list_documents():
    # фильтрация по теме (category)
    category = request.args.get('category')
    q = request.args.get('q')
    query = Document.query
    if category:
        query = query.filter_by(category=category)
    if q:
        query = query.filter(Document.title.contains(q) | Document.description.contains(q))
    docs = query.all()
    return DocumentSchema(many=True).jsonify(docs)

@documents_bp.route('/documents/<int:id>/download', methods=['GET'])
def download_document(id):
    doc = Document.query.get_or_404(id)
    if doc.file_path and os.path.exists(doc.file_path):
        return send_file(doc.file_path, as_attachment=True)
    elif doc.external_link:
        return jsonify({'link': doc.external_link})
    else:
        return jsonify({'error': 'File not found'}), 404

