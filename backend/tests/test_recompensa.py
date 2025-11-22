def test_get_recompensas(client, auth_headers):
    resp = client.get('/api/recompensas', headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_get_mis_recompensas(client, auth_headers):
    resp = client.get('/api/recompensas/mis-recompensas', headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)