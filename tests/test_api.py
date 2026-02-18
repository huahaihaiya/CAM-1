import json
import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_predict_validation(client):
    r = client.post('/predict', json={})
    assert r.status_code == 400
    r = client.post('/predict', json={'smiles1':'CCO','smiles2':'', 'method':1, 'ratio':1.0})
    assert r.status_code == 400
    r = client.post('/predict', json={'smiles1':'CCO','smiles2':'CCN', 'method':3, 'ratio':1.0})
    assert r.status_code == 400
    r = client.post('/predict', json={'smiles1':'CCO','smiles2':'CCN', 'method':1, 'ratio':0})
    assert r.status_code == 400

def test_analyze_validation(client):
    r = client.post('/analyze', json={})
    assert r.status_code == 400
    r = client.post('/analyze', json={'smiles1':'CCO','smiles2':'CCN','prediction':2})
    assert r.status_code == 400