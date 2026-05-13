def test_submit_masterclass_pass(client, user_token, masterclass):
    start = client.post(f'/api/masterclasses/{masterclass.id}/start',
                        headers={'Authorization': f'Bearer {user_token}'})
    # Собираем правильные ответы: для каждого теста находим индекс, где is_correct == True
    answers = {}
    for test in masterclass.tests:
        correct_index = next(i for i, opt in enumerate(test.options) if opt['is_correct'])
        answers[str(test.id)] = correct_index
    
    resp = client.post(f'/api/masterclasses/{masterclass.id}/submit',
                       headers={'Authorization': f'Bearer {user_token}'},
                       json={'answers': answers})
    assert resp.status_code == 200
    assert resp.json['score'] == 100.0

def test_submit_masterclass_fail(client, user_token, masterclass):
    client.post(f'/api/masterclasses/{masterclass.id}/start',
                headers={'Authorization': f'Bearer {user_token}'})
    # Все ответы – первый вариант (неправильный, если правильный не под индексом 0)
    answers = {str(test.id): 0 for test in masterclass.tests}
    resp = client.post(f'/api/masterclasses/{masterclass.id}/submit',
                       headers={'Authorization': f'Bearer {user_token}'},
                       json={'answers': answers})
    assert resp.status_code == 200
    # Если ни один ответ не правильный, score должен быть 0.0
    assert resp.json['score'] == 0.0