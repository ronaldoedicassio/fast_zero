from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_read_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # Arrange (organização)
    responde = client.get('/')  # Act (ação)
    assert responde.status_code == HTTPStatus.OK  # Assert (afirmação)
    assert responde.json() == {'message': 'Olá Mundo'}
