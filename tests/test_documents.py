from app.models import User, Document, Appeal, Webinar, WebinarView,  MasterClass, Test, MasterClassProgress, Certificate, Survey, SurveyQuestion, SurveyResponse
def test_list_documents_empty(client, db):   # добавлен db
    resp = client.get('/api/documents')
    assert resp.status_code == 200
    assert isinstance(resp.json, list)
    assert len(resp.json) == 0

def test_list_documents_with_filter(client, db):
    doc = Document(title='Law on Education', category='law')
    db.session.add(doc)
    db.session.commit()
    resp = client.get('/api/documents?category=law')
    assert len(resp.json) == 1
    assert resp.json[0]['title'] == 'Law on Education'