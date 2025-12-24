import os
import tempfile
import pytest
from app import app

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    yield client
    os.close(db_fd)
    os.unlink(db_path)

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'C++ Quiz' in rv.data

def test_admin_login_page(client):
    rv = client.get('/admin')
    assert rv.status_code == 200
    assert b'Admin' in rv.data

def test_admin_login_fail(client):
    rv = client.post('/admin/login', data={'password': 'wrong'})
    assert b'Invalid password' in rv.data

def test_admin_login_success(client):
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess['admin_logged_in'] = True
        rv = c.get('/admin/panel')
        assert rv.status_code == 200
        assert b'Admin Panel' in rv.data
