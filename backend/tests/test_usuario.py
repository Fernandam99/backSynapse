from app.models.usuario import Usuario 

def test_get_all_users(client, auth_headers):
    resp = client.get('/api/usuarios', headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_get_user_by_id(client, auth_headers, db):
    user = db.session.query(Usuario).filter_by(correo='test@example.com').first()
    resp = client.get(f'/api/usuarios/{user.id_usuario}', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['correo'] == 'test@example.com'

def test_create_user(client, auth_headers):
    resp = client.post('/api/usuarios', json={
        'Username': 'createduser',
        'correo': 'created@example.com',
        'password': 'Pass123!',
        'rol_id': 1
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()['correo'] == 'created@example.com'

def test_update_user(client, auth_headers, db):
    user = db.session.query(Usuario).filter_by(correo='test@example.com').first()
    resp = client.put(f'/api/usuarios/{user.id_usuario}', json={
        'correo': 'updated@example.com'
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['correo'] == 'updated@example.com'

def test_delete_user(client, auth_headers, db):
    user = db.session.query(Usuario).filter_by(correo='test@example.com').first()
    resp = client.delete(f'/api/usuarios/{user.id_usuario}', headers=auth_headers)
    assert resp.status_code == 200
    # La API hace soft-delete
    updated = db.session.query(Usuario).get(user.id_usuario)
    assert updated.activo is False