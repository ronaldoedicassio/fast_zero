from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

# Importações para SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Token
from fast_zero.security import create_access_token, verify_password


router = APIRouter(prefix='/auth', tags=['auth'])


Session = Annotated[Session, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
# Endpoint para autenticação e geração de token de acesso. Retorna o token de acesso. no modelo de resposta Token
def login_for_acess_token(form_data: OAuth2Form, session: Session):
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

