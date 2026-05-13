def test_register(client, db):
    resp = client.post('/api/register', json={
        'email': 'new@test.com',
        'password': 'newpass',
        'full_name': 'New User'
    })
    assert resp.status_code == 201
    assert resp.json['message'] == 'User created'

def test_register_duplicate(client, user):
    resp = client.post('/api/register', json={
        'email': user.email,
        'password': 'newpass',
        'full_name': 'Another'
    })
    assert resp.status_code == 400
    assert 'Email already exists' in resp.json['error']

def test_login(client, user):
    resp = client.post('/api/login', json={
        'email': user.email,        # 'duplicate@example.com'
        'password': 'secret'
    })
    assert resp.status_code == 200
def test_login_invalid(client):
    resp = client.post('/api/login', json={
        'email': 'wrong@test.com',
        'password': 'wrong'
    })
    assert resp.status_code == 401

def test_profile_requires_auth(client):
    resp = client.get('/api/profile')
    assert resp.status_code == 401

def test_profile_valid(client, user_token):
    resp = client.get('/api/profile', headers={'Authorization': f'Bearer {user_token}'})
    assert resp.status_code == 200
    assert resp.json['email'] == 'user@test.com'