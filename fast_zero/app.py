from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException

# Importações para SQLAlchemy
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema

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

    db_user = User(username=user.username, password=user.password, email=user.email)  # Cria um novo objeto User com os dados fornecidos.

    session.add(db_user)  # Adiciona o objeto User à sessão de banco de dados.
    session.commit()  # Salva as alterações no banco de dados.
    session.refresh(db_user)  # Atualiza o objeto User com os dados do banco de dados, incluindo o ID gerado automaticamente.

    return db_user  # Retorna o objeto User atualizado.


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    offset: int = 0,  # paginação para limitar a quantidade de registros retornados e pular os primeiros registros
    session: Session = Depends(get_session),
):  # Usando dependência para obter a sessão de banco de dados.
    users = session.scalars(select(User).limit(limit).offset(offset))
    # Usa a sessão de banco de dados para selecionar todos os usuários.
    # session.scalars => Retorna todos os resultados como uma lista de objetos User.
    # limit => limita a quantidade de registros retornados
    # offset => pula os primeiros registros
    return {'users': users}


@app.put('/users/{user_id}', response_model=UserPublic)
# Atualiza um usuário existente com base no ID fornecido. Retorna o usuário atualizado.
def update_user(user_id: int, user: UserSchema, session: Session = Depends(get_session)):
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
        user_db.password = user.password

        session.add(user_db)
        session.commit()
        session.refresh(user_db)

        return user_db

    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username or email already exists')


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_db = session.scalar(select(User).where(User.id == user_id))

    if not user_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    session.delete(user_db)
    session.commit()

    return {'message': 'User deleted successfully'}


# ***** CODIGO COMENTADO PARA NÃO PERDER HISTÓRICO DE EVOLUCAO *****
""" @app.get('/users/', response_model=UserList)
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
