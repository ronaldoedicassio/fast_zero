from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.settings import Settings

pwd_context = PasswordHash.recommended()
settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
    # Verifica se a senha em texto simples corresponde ao hash armazenado.


def create_access_token(data: dict):
    # Função para criar um token de acesso JWT.
    to_encode = data.copy()
    # Copia os dados fornecidos para evitar modificar o original.
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Calcula o tempo de expiração do token.
    to_encode.update({'exp': expire})
    # Adiciona o tempo de expiração aos dados a serem codificados.
    encoded_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    # Codifica os dados em um token JWT usando a chave secreta e o algoritmo especificado.
    return encoded_jwt
    # Retorna o token JWT gerado.


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'}
    )
    # Exceção a ser levantada em caso de falha na validação das credenciais.
    # Usa dependência para obter a sessão de banco de dados e o token OAuth2.
    # headers={'WWW-Authenticate': 'Bearer'} => informa ao cliente que ele deve usar o esquema de autenticação Bearer.
    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Decodifica o token JWT usando a chave secreta e o algoritmo especificado enviado.
        # Se o token for inválido ou expirado, uma exceção DecodeError será levantada.
        subject_email = payload.get('sub')
        # Extrai o email do assunto (sub) do token decodificado.
        if not subject_email:
            # Se o email do assunto não estiver presente, levanta uma exceção HTTP 401.
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == subject_email))
    # Busca o usuário no banco de dados com base no email extraído do token.

    if not user:
        raise credentials_exception
        # Se o usuário não for encontrado, levanta uma exceção HTTP 401.

    return user
