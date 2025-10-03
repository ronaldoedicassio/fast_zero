from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

# Importações para SQLAlchemy
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, Token, UserList, UserPublic, UserSchema
from fast_zero.security import create_access_token, get_current_user, get_password_hash, verify_password

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(
    user: UserSchema, session=Depends(get_session)
):  # Usando dependência para obter a sessão de banco de dados após usar ele encerra conexão com o banco.
    # engine = create_engine(Settings().DATABASE_URL)
    # # Cria a engine de conexão com o banco de dados usando a URL do banco de dados das configurações.
    # session = Session(engine)  # Cria uma sessão de banco de dados usando a engine criada.
    # linhas acima foi comentada para usar a engine do database.py

    # session = get_session()  # Usa a função get_session do database.py para obter uma sessão de banco de dados.
    # session e requisito para fazer operações no banco de dados com SQLAlchemy para isso vamos usar dependência do FastAPI
    # Porém essa forma de chamar a função não é a ideal, pois a cada requisição uma nova conexão com o banco de dados será criada
    # e não será fechada, o ideal é usar a injeção de dependência

    db_user = session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )  # Seleciona o usuário do banco de dados com o ID fornecido.
    # o Scalar vai retornar o primeiro resultado ou None ou se encontrou um resultado, somente um resultado, se for mais de um serai scalars

    if db_user:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or email already exists')

    db_user = User(username=user.username, password=get_password_hash(user.password), email=user.email)
    # Cria um novo objeto User com os dados fornecidos.

    session.add(db_user)  # Adiciona o objeto User à sessão de banco de dados.
    session.commit()  # Salva as alterações no banco de dados.
    session.refresh(db_user)  # Atualiza o objeto User com os dados do banco de dados, incluindo o ID gerado automaticamente.

    return db_user  # Retorna o objeto User atualizado.


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    offset: int = 0,  # paginação para limitar a quantidade de registros retornados e pular os primeiros registros
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    # Usando dependência para obter o usuário atual autenticado. tem que ter um usuário autenticado para acessar esse endpoint
):  # Usando dependência para obter a sessão de banco de dados.
    users = session.scalars(select(User).limit(limit).offset(offset))
    # Usa a sessão de banco de dados para selecionar todos os usuários.
    # session.scalars => Retorna todos os resultados como uma lista de objetos User.
    # limit => limita a quantidade de registros retornados
    # offset => pula os primeiros registros
    return {'users': users}


@app.put('/users/{user_id}', response_model=UserPublic)
# Atualiza um usuário existente com base no ID fornecido. Retorna o usuário atualizado.
def update_user(user_id: int, user: UserSchema, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Agora com o current_user não sera preciso comparar o usuário, pois a propria funçao ja faz essa validação
    # Usando dependência para obter a sessão de banco de dados.
    # user_id é o ID do usuário a ser atualizado.
    # user é o objeto UserSchema com os dados atualizados.
    # session é a sessão de banco de dados pela injeção de dependência.
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission')

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)
        # Atualiza os campos do usuário com os dados fornecidos, incluindo o hash da nova senha.

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or email already exists')


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # passando o currente user, não sera mais necessário buscar o usuario no bano
    # user_db = session.scalar(select(User).where(User.id == user_id))

    # if not user_db:
    #    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    if current_user.id != user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not enough permission')

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted successfully'}


@app.post('/token', response_model=Token)
# Endpoint para autenticação e geração de token de acesso. Retorna o token de acesso. no modelo de resposta Token
def login_for_acess_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # OAuth2PasswordRequestForm => Formulário de dados enviado pelo cliente para autenticação.
    # Ele espera receber os campos username e password no corpo da requisição.
    user = session.scalar(select(User).where(User.email == form_data.username))
    # Busca o usuário no banco de dados com base no email fornecido no formulário.
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )
    # caso envie um token diferente do JWT
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )
    access_token = create_access_token(data={'sub': user.email})
    # Cria um token de acesso JWT com o email do usuário como assunto (sub).
    return {'access_token': access_token, 'token_type': 'Bearer'}


# ***** CODIGO COMENTADO PARA NÃO PERDER HISTÓRICO DE EVOLUCAO *****

""" @app.put('/users/{user_id}', response_model=UserPublic)
# Atualiza um usuário existente com base no ID fornecido. Retorna o usuário atualizado.

def update_user(user_id: int, user: UserSchema, session: Session = Depends(get_session)):
    Funcão atualiza sem current_user
    # Usando dependência para obter a sessão de banco de dados.
    # user_id é o ID do usuário a ser atualizado.
    # user é o objeto UserSchema com os dados atualizados.
    # session é a sessão de banco de dados pela injeção de dependência.
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    try:
        user_db.username = user.username
        user_db.email = user.email
        user_db.password = get_password_hash(user.password)
        # Atualiza os campos do usuário com os dados fornecidos, incluindo o hash da nova senha.

        session.add(user_db)
        session.commit()
        session.refresh(user_db)

        return user_db

    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or email already exists')

    @app.get('/users/', response_model=UserList)
    def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
        # Usando dependência para obter a sessão de banco de dados.
        users = session.scalars(select(User).offset(skip).limit(limit)).all()
        Usa a sessão de banco de dados para selecionar todos os usuários, aplicando os parâmetros de paginação skip e limit.
        session.scalars => Retorna todos os resultados como uma lista de objetos User.
        return {'users': users}

    @app.delete('/users/{user_id}', response_model=Message)
    def delete_user(user_id: int):
       if user_id > len(database) or user_id < 1:
           raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
       del database[user_id - 1]
       return {'message': 'User deleted'}


    @app.put('/users/{user_id}', response_model=UserPublic)
    def update_user(user_id: int, user: UserSchema):
        Aqui esta o codigo antigo antes de mudar para SQLAlchemy
        if user_id < 1 or user_id > len(database):
            raise HTTPStatus(HTTPStatus.NOT_FOUND, detail='User not found')

        user_with_id = UserDB(**user.model_dump(), id=user_id)
        database[user_id - 1] = user_with_id

        return user_with_id
    @app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
    def create_user(user: UserSchema):
        user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)

        # **user.model_dump() -> Desempacota os atributos do user
        # Em vez de passar todos os campos de user no formato
        # user=user.username,
        # email=user.email,
        # password=user.password
        # Dessa passando os campos desempacotados pela função model_dump()
        # CAbeçario de função da live explicação melhor o conteudo

        database.append(user_with_id)
        return user_with_id

    """
