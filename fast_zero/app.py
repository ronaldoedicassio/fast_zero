from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from http import HTTPStatus
from pydantic import UserPublic
app = FastAPI()


@app.get('/')
def read_root():
    return {'message': 'Olá Mundo'}

@app.get('/exercicio-html', response_class=HTMLResponse)
def exercicio_aula_02():
    return """
    <html>
      <head>
        <title>Nosso olá mundo!</title>
      </head>
      <body>
        <h1> Olá Mundo </h1>
      </body>
    </html>"""

@app.get('/users/{user_id}', response_model=UserPublic)
def read_user(user_id: int):
    # Busca o usuário pelo ID em toda a lista
    user = next((user for user in database if user.get('id') == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, 
            detail='User not found'
        )
    
    return user