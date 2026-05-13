def test_create_appeal(client, user_token):
    resp = client.post('/api/appeals',
                       headers={'Authorization': f'Bearer {user_token}'},
                       json={
                           'full_name': 'Test User',
                           'topic': 'Question',
                           'message': 'Help please'
                       })
    assert resp.status_code == 201

def test_get_appeals_user(client, user_token, db):
    
    client.post('/api/appeals', headers={'Authorization': f'Bearer {user_token}'},
                json={'full_name': 'Test','topic':'T','message':'M'})
    resp = client.get('/api/appeals', headers={'Authorization': f'Bearer {user_token}'})
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['status'] == 'new'

def test_admin_can_see_all_appeals(client, admin_token, user_token, db):
    client.post('/api/appeals', headers={'Authorization': f'Bearer {user_token}'},
                json={'full_name':'User','topic':'T','message':'M'})
    resp = client.get('/api/appeals', headers={'Authorization': f'Bearer {admin_token}'})
    assert len(resp.json) == 1