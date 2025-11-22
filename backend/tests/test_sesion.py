def test_create_session(client, auth_headers, db):
    # Asegurar que existe la técnica "Pomodoro"
    from app.models.tecnica import Tecnica
    pomodoro = db.session.query(Tecnica).filter_by(nombre='Pomodoro').first()
    if not pomodoro:
        pomodoro = Tecnica(nombre='Pomodoro', categoria='productividad')
        db.session.add(pomodoro)
        db.session.commit()

    resp = client.post('/api/sesiones', json={
        'tecnica_id': pomodoro.id_tecnica,
        'estado': 'Completado',
        'duracion_real': 25
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()['tecnica_id'] == pomodoro.id_tecnica

def test_get_sessions(client, auth_headers):
    resp = client.get('/api/sesiones', headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)