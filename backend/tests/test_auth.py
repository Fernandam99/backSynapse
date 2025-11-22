def test_register_success(client, db):
    resp = client.post('/api/auth/register', json={
        'username': 'newuser',
        'correo': 'new@example.com',
        'password': 'ValidPass123!'
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'usuario' in data
    assert data['usuario']['correo'] == 'new@example.com'

def test_login_success(client, db):
    resp = client.post('/api/auth/login', json={
        'correo': 'test@example.com',
        'password': 'SecurePass123!'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'access_token' in data
    assert 'usuario' in data

def test_login_fail_wrong_password(client, db):
    resp = client.post('/api/auth/login', json={
        'correo': 'test@example.com',
        'password': 'WrongPass!'
    })
    assert resp.status_code == 401

def test_get_current_user(client, auth_headers):
    resp = client.get('/api/auth/me', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['correo'] == 'test@example.com'