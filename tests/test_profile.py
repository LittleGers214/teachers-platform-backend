def test_get_certificates_empty(client, user_token):
    resp = client.get('/api/profile/certificates', headers={'Authorization': f'Bearer {user_token}'})
    assert resp.json == []

def test_get_progress(client, user_token, masterclass):
    # после успешного прохождения мастер-класса прогресс должен отразиться
    # сначала стартуем и проходим
    client.post(f'/api/masterclasses/{masterclass.id}/start',
                headers={'Authorization': f'Bearer {user_token}'})
    answers = {
        str(masterclass.tests[0].id): 1,
        str(masterclass.tests[1].id): 2
    }
    client.post(f'/api/masterclasses/{masterclass.id}/submit',
                headers={'Authorization': f'Bearer {user_token}'},
                json={'answers': answers})
    resp = client.get('/api/profile/progress', headers={'Authorization': f'Bearer {user_token}'})
    assert resp.status_code == 200
    assert len(resp.json['masterclasses']) == 1
    assert resp.json['masterclasses'][0]['passed'] is True