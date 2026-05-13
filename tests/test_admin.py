import io
def test_admin_upload_document(client, admin_token, clean_db):
    headers = {'Authorization': f'Bearer {admin_token}'}
    # Для загрузки файла используем multipart/form-data
    data = {
        'title': 'Test Doc',
        'description': 'Test description',
        'category': 'law',
        'file': (io.BytesIO(b'%PDF-1.4 fake content'), 'test.pdf')
    }
    resp = client.post('/api/admin/documents', data=data, headers=headers, content_type='multipart/form-data')
    # Ожидаем 201 Created или 200 OK
    assert resp.status_code in (200, 201)
    assert 'id' in resp.json or 'message' in resp.json

def test_non_admin_cannot_upload(client, user_token, clean_db):
    headers = {'Authorization': f'Bearer {user_token}'}
    data = {
        'title': 'Test Doc',
        'file': (io.BytesIO(b'content'), 'test.pdf')
    }
    resp = client.post('/api/admin/documents', data=data, headers=headers, content_type='multipart/form-data')
    assert resp.status_code == 403
    assert 'error' in resp.json

def test_admin_create_masterclass(client, admin_token, clean_db):
    headers = {'Authorization': f'Bearer {admin_token}'}
    payload = {
        'title': 'Python for Teachers',
        'description': 'Learn Python basics',
        'passing_score': 85
    }
    resp = client.post('/api/admin/masterclasses', json=payload, headers=headers)
    assert resp.status_code == 201
    assert 'id' in resp.json