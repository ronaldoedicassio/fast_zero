from http import HTTPStatus

from fast_zero.schemas import UserPublic

# importa para converter o objeto user (instância do modelo ORM User) em um dicionário usando o Pydantic UserPublic.


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    # client = TestClient(app)  # Arrange (organização)
    # => foi colocado passando o client como fixture
    responde = client.get('/')  # Act (ação)
    assert responde.status_code == HTTPStatus.OK  # Assert (afirmação)
    assert responde.json() == {'message': 'Olá Mundo'}


def test_create_user_deve_retornar_created_user_200(client):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@exemplo.com',
            'password': 'senha123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@exemplo.com',
    }


def test_create_user_deve_retornar_created_user_409(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'Teste',
            'email': 'teste@test.com',
            'password': 'testtest',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_read_users_deve_retornar_ok_e_lista_sem_usuarios_vazia(client):
    # Primeiro, criar alguns usuários para garantir que a lista não esteja vazia
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_deve_retornar_ok_e_lista_com_usuarios(client, user):
    # Primeiro, criar alguns usuários para garantir que a lista não esteja vazia
    user_schema = UserPublic.model_validate(user).model_dump()
    # converte o objeto user (instância do modelo ORM User) em um dicionário usando o Pydantic UserPublic.
    # Isso é necessário porque a resposta JSON do endpoint será um dicionário, e queremos compará-lo com a resposta da API.

    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_upadate_user(client, user):
    # user é o fixture que cria um usuário de teste no banco de dados em memória.
    response = client.put(
        '/users/1',
        json={
            'username': 'alice_updated',
            'email': 'alice_updated@example.com',
            'password': 'newpassword123',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice_updated',
        'email': 'alice_updated@example.com',
    }


def test_upadate_user_409(client, user):
    # user é o fixture que cria um usuário de teste no banco de dados em memória.
    response = client.put(
        '/users/111',
        json={
            'username': 'alice_updated',
            'email': 'alice_updated@example.com',
            'password': 'newpassword123',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_upadate_user_conflict_name_email(client, user):
    # user é o fixture que cria um usuário de teste no banco de dados em memória.
    # Inserindo fausto
    client.post(
        '/users',
        json={
            'username': 'Teste1',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'Teste1',
            'email': 'teste_teste@test.com',
            'password': 'newpassword123',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_delete_user_409(client, user):
    # user é o fixture que cria um usuário de teste no banco de dados em memória.
    response = client.delete('/users/111')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, user):
    # user é o fixture que cria um usuário de teste no banco de dados em memória.
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}
