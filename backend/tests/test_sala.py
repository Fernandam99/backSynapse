def test_create_sala(client, auth_headers):
    resp = client.post('/api/salas', json={
        'nombre': 'Sala de Estudio',
        'descripcion': 'Prueba de integración',
        'es_privada': False
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()['nombre'] == 'Sala de Estudio'

def test_get_my_salas(client, auth_headers):
    resp = client.get('/api/salas', headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)