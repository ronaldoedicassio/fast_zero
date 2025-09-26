from http import HTTPStatus

from fastapi import FastAPI,HTTPException

from fast_zero.schemas import Message,UserPublic

app = FastAPI()

# DATABASE CORRIGIDO - IDs devem ser consistentes
database = [
    {"id": 1, "username": "john", "email": "john@example.com"},
    {"id": 2, "username": "jane", "email": "jane@example.com"},
]


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo'}

@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int):
    # Busca o usuário pelo ID
    user = next((user for user in database if user.get('id') == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, 
            detail='User not found'
        )
    
    return user