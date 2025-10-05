from http import HTTPStatus

# importa para converter o objeto user (instância do modelo ORM User) em um dicionário usando o Pydantic UserPublic.


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    # client = TestClient(app)  # Arrange (organização)
    # => foi colocado passando o client como fixture
    responde = client.get('/')  # Act (ação)
    assert responde.status_code == HTTPStatus.OK  # Assert (afirmação)
    assert responde.json() == {'message': 'Olá Mundo'}


"""'
FUNÇÕES ABAIXO NÃO FAZEM PARTE DA REGRA DE NEGÓCIO, FORAM APAGADAS, MAS DEIXADAS AQUI PARA NÃO PERDER O HISTÓRICO DE EVOLUÇÃO DO CÓDIGO.

def test_read_users_deve_retornar_ok_e_lista_sem_usuarios_vazia(client):
    # Primeiro, criar alguns usuários para garantir que a lista não esteja vazia
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}
"""
