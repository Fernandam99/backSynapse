from datetime import date
from app.models.usuario import Usuario # <-- Corrección clave: Importar Usuario

def test_create_task(client, auth_headers, db):
    user = db.session.query(Usuario).filter_by(correo='test@example.com').first()
    resp = client.post('/api/tareas', json={
        'titulo': 'Estudiar Flask',
        'descripcion': 'Hacer tests de integración',
        'fecha_vencimiento': str(date.today()),
        'prioridad': 'alta'
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['titulo'] == 'Estudiar Flask'
    assert data['usuario_id'] == user.id_usuario

def test_get_tasks(client, auth_headers):
    resp = client.get('/api/tareas', headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_update_task(client, auth_headers, db):
    resp = client.post('/api/tareas', json={
        'titulo': 'Tarea para actualizar',
        'descripcion': 'Test',
        'fecha_vencimiento': str(date.today()),
        'prioridad': 'baja'
    }, headers=auth_headers)
    task_id = resp.get_json()['id_tarea']

    resp2 = client.put(f'/api/tareas/{task_id}', json={
        'estado': 'Completado'
    }, headers=auth_headers)
    assert resp2.status_code == 200
    assert resp2.get_json()['estado'] == 'Completado'

def test_delete_task(client, auth_headers, db):
    resp = client.post('/api/tareas', json={
        'titulo': 'Tarea para eliminar',
        'descripcion': 'Test',
        'fecha_vencimiento': str(date.today()),
        'prioridad': 'baja'
    }, headers=auth_headers)
    task_id = resp.get_json()['id_tarea']

    resp2 = client.delete(f'/api/tareas/{task_id}', headers=auth_headers)
    assert resp2.status_code == 200