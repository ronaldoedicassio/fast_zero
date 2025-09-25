from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_read_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)  # Arrange (organização)
    responde = client.get('/')  # Act (ação)
    assert responde.status_code == HTTPStatus.OK  # Assert (afirmação)
    assert responde.json() == {'message': 'Olá Mundo'}


def test_exercicio_aula_02_deve_retornar_html_com_ola_mundo():
    client = TestClient(app)  # Arrange (organização)
    response = client.get('/exercicio-html')  # Act (ação)
    assert response.status_code == HTTPStatus.OK  # Assert (afirmação)
    assert '<h1> Olá Mundo </h1>' in response.text


def test_upadade_user_deve_retornar_404_quando_usuario_nao_existir():
    client = TestClient(app)  # Arrange (organização)
    response = client.put('/users/999', json={'name': 'Novo Nome'})  # Act (ação)
    assert response.status_code == HTTPStatus.NOT_FOUND  # Assert (afirmação)
    assert response.json() == {'detail': 'User not found'}
