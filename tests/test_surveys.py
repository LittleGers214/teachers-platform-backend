import pytest
from app.models import Survey, SurveyQuestion

def test_list_surveys(client, user_token, db):
    s = Survey(title='Test Survey', is_active=True, is_required=True)
    db.session.add(s)
    db.session.commit()
    resp = client.get('/api/surveys', headers={'Authorization': f'Bearer {user_token}'})
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['is_completed'] is False

def test_submit_survey(client, user_token, db):
    s = Survey(title='Test Survey', is_active=True)
    db.session.add(s)
    db.session.commit()
    q = SurveyQuestion(survey_id=s.id, question_text='Rate?', question_type='radio', options=['1','2','3'])
    db.session.add(q)
    db.session.commit()
    resp = client.post(f'/api/surveys/{s.id}/submit',
                       headers={'Authorization': f'Bearer {user_token}'},
                       json={'answers': {str(q.id): '2'}})
    assert resp.status_code == 200
    # повторная отправка должна быть заблокирована
    resp2 = client.post(f'/api/surveys/{s.id}/submit',
                        headers={'Authorization': f'Bearer {user_token}'},
                        json={'answers': {}})
    assert resp2.status_code == 400
    assert 'Already responded' in resp2.json['error']