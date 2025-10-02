from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user_db(session, mock_db_time):
    with mock_db_time(model=User) as time:  # Inicia o gerenciador de contexto mock_db_time usando o modelo User como base.
        new_user = User(username='alice', password='secret', email='teste@test')
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))

    assert asdict(user) == {  # Converte o user em um dicionário para simplificar a validação no teste.
        'id': 1,
        'username': 'alice',
        'password': 'secret',
        'email': 'teste@test',
        'created_at': time,  # Usa o time gerado por mock_db_time para validar o campo created_at.
        'updated_at': time,  # Exercício
    }
