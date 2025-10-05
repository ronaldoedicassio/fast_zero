from http import HTTPStatus

from jwt import decode

from fast_zero.security import create_access_token, settings


def test_jwt():
    data = {'test': 'test'}

    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    # Decodifica o token JWT usando a chave secreta e o algoritmo especificado.
    assert decoded['test'] == data['test']
    # Verifica se o valor decodificado corresponde ao valor original.
    assert 'exp' in decoded
    # Verifica se o campo de expiração (exp) está presente no token decodificado.


def test_jwt_invalid_token(client):
    response = client.delete('/users/1', headers={'Authorization': 'Bearer token-invalido'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_user_not_found(client):
    data = {'no-email': 'test'}

    response = client.delete('users/1', headers={'Authorization': f'Bearer {create_access_token(data)}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_does_not_exists__exercicio(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/11',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_wrong_username(client, token):
    response = client.post(
        '/auth/token',
        headers={'Authorization': f'Bearer {token}'},
        data={
            'username': 'Teste',
            'password': 'newpassword1232222',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_login_wrong_password(client, user_with_password):
    # tentativa de login com senha errada
    response = client.post(
        '/auth/token',  # essa é a rota definida no teu @app.post('/token')
        data={
            'username': user_with_password.email,  # atenção: teu código usa email aqui!
            'password': 'senha_errada',  # senha incorreta
        },
    )

    # deve cair no raise HTTPException 401
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_user_access_forbidden(client, token):
    response = client.put(
        '/users/111',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'alice_updated',
            'email': 'alice_updated@example.com',
            'password': 'newpassword123',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}


def test_user_delete_forbidden(client, token):
    response = client.delete('/users/111', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}
