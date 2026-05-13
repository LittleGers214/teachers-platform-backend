def test_mark_webinar_viewed(client, user_token, clean_db, webinar):
    headers = {'Authorization': f'Bearer {user_token}'}
    resp = client.post(f'/api/webinars/{webinar.id}/view', headers=headers)
    assert resp.status_code == 200