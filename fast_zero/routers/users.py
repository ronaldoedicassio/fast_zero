from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

# Importações para SQLAlchemy
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import FilterPage, Message, UserList, UserPublic, UserSchema
from fast_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session):
    # Usando dependência para obter a sessão de banco de dados após usar ele encerra conexão com o banco.
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

    hashed_password = get_password_hash(user.password)
    # encriptografa a senha e salva no banco
    db_user = User(username=user.username, password=hashed_password, email=user.email)
    # Cria um novo objeto User com os dados fornecidos.

    session.add(db_user)  # Adiciona o objeto User à sessão de banco de dados.
    session.commit()  # Salva as alterações no banco de dados.
    session.refresh(db_user)  # Atualiza o objeto User com os dados do banco de dados, incluindo o ID gerado automaticamente.

    return db_user  # Retorna o objeto User atualizado.


@router.get('/', response_model=UserList)
def read_users(session: Session, current_user: CurrentUser, filter_users: Annotated[FilterPage, Query()]):
    # filter_users-> paginação para limitar a quantidade de registros retornados e pular os primeiros registros
    # Usando dependência para obter o usuário atual autenticado. tem que ter um usuário autenticado para acessar esse endpoint
    # Usando dependência para obter a sessão de banco de dados.
    users = session.scalars(select(User).offset(filter_users.offset).limit(filter_users.limit)).all()

    # Usa a sessão de banco de dados para selecionar todos os usuários.
    # session.scalars => Retorna todos os resultados como uma lista de objetos User.
    # limit => limita a quantidade de registros retornados
    # offset => pula os primeiros registros
    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
# Atualiza um usuário existente com base no ID fornecido. Retorna o usuário atualizado.
def update_user(user_id: int, user: UserSchema, session: Session, current_user: CurrentUser):
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


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
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
