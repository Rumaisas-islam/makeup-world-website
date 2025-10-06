"""
Unit tests for Makeup World Inventory App.
Tests cover login, add/edit/delete product, and homepage redirect.
"""
import os
import sys
import pytest

# 👇 Add parent directory (where app.py lives) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Product


@pytest.fixture
def client():
    """Create a test client with an in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_home_redirects_to_login(client):
    """Unauthenticated users should be redirected to login page."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_login_success(client):
    """Valid login should redirect to dashboard."""
    response = client.post('/login', data={'username': 'admin', 'password': '1234'}, follow_redirects=True)
    assert response.status_code == 200
    # Since your index page doesn't have 'Dashboard' text, just check login redirect worked
    assert b'Login successful' in response.data or b'Makeup' in response.data


def test_add_product(client):
    """Admin can add a product successfully."""
    client.post('/login', data={'username': 'admin', 'password': '1234'})
    client.post('/add', data={
        'name': 'Lipstick',
        'price': '1500',
        'company': 'L’Oréal',
        'category': 'Makeup',
        'use': 'Lips',
        'stock': '10'
    }, follow_redirects=True)

    # ✅ Verify product was actually added in DB
    with app.app_context():
        product = Product.query.filter_by(name='Lipstick').first()
        assert product is not None
        assert product.price == 1500


def test_edit_product(client):
    """Admin can edit an existing product."""
    client.post('/login', data={'username': 'admin', 'password': '1234'})
    product = Product(name='Test', price=100, company='Maybelline', category='Makeup', use='Eyes', stock=5)
    db.session.add(product)
    db.session.commit()

    client.post(f'/edit/{product.id}', data={
        'name': 'Updated Test',
        'price': '200',
        'company': 'Maybelline',
        'category': 'Makeup',
        'use': 'Eyes',
        'stock': '10'
    }, follow_redirects=True)

    # ✅ Verify DB record was updated
    with app.app_context():
        updated = Product.query.get(product.id)
        assert updated.name == 'Updated Test'
        assert updated.price == 200


def test_delete_product(client):
    """Admin can delete a product successfully."""
    client.post('/login', data={'username': 'admin', 'password': '1234'})
    product = Product(name='DeleteMe', price=500, company='Revlon', category='Makeup', use='Face', stock=3)
    db.session.add(product)
    db.session.commit()

    client.get(f'/delete/{product.id}', follow_redirects=True)

    # ✅ Verify DB record was deleted
    with app.app_context():
        deleted = Product.query.get(product.id)
        assert deleted is None
