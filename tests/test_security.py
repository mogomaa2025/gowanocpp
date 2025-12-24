import os
from app import app

def test_admin_password_env():
    assert os.environ.get('ADMIN_PASSWORD', None) is not None
    assert app.config['SECRET_KEY'] != 'your-secret-key-change-this'
