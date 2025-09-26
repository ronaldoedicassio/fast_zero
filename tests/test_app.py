from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_read_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # Arrange (organização)
    responde = client.get('/')  # Act (ação)
    assert responde.status_code == HTTPStatus.OK  # Assert (afirmação)
    assert responde.json() == {'message': 'Olá Mundo'}

def test_read_user_existing():
    client = TestClient(app)
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'john',
        'email': 'john@example.com'
    }

def test_read_user_not_found():
    client = TestClient(app)
    response = client.get('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}