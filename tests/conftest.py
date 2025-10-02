from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry


@pytest.fixture  # Fixture do pytest que cria um cliente de teste para a aplicação FastAPI.
def client(session):
    # session é uma fixture que cria uma sessão de banco de dados em memória.
    # Ira sobreescrever a dependência get_session do app para usar o banco de dados em memória.
    # Forçando o uso do banco de dados em memória e resetando os dados a cada teste.
    def get_session_override():
        # Ira sobreescrever a dependência get_session do app para usar o banco de dados em memória.
        # Forçando o uso do banco de dados em memória e resetando os dados a cada teste.
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        # Sobrescreve a dependência get_session do app para usar a função get_session_override.
        # Isso faz com que o app use a sessão do banco de dados em memória para os testes.
        yield client

    app.dependency_overrides.clear()
    # Limpa as substituições de dependência após o teste.


@pytest.fixture
def session():
    engine = create_engine(
        # create_engine('sqlite:///./test.db', echo=True) # echo=True => Habilita o log de todas as operações SQL executadas pela engine.
        # engine e engrenagem de conexão com o banco de dados.
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        # false para permitir que a conexão seja compartilhada entre diferentes threads.
        poolclass=StaticPool,
    )
    # poolclass=StaticPool => garante que a mesma conexão será usada em todas as sessões para diferentes threads.
    # connect_args={'check_same_thread': False} => Permite que a conexão seja compartilhada entre diferentes threads.
    # 'sqlite:///:memory:' => Cria um banco de dados SQLite em memória que é volátil e será perdido quando a conexão for fechada.

    table_registry.metadata.create_all(engine)
    # Cria todas as tabelas no banco de dados em memória.

    with Session(engine) as session:
        # Usa a sessão para fazer operações no banco de dados.
        yield session

    session.close()
    # encerra a sessão
    engine.dispose()
    # Fecha a sessão e a conexão com o banco de dados.
    engine.dispose()
    # encerrar a engine de conexão com o banco de dados.
    table_registry.metadata.drop_all(engine)
    # Remove todas as tabelas do banco de dados em memória após o teste.


@contextmanager  # O decorador @contextmanager cria um gerenciador de contexto para que a função _mock_db_time seja usada com um bloco with.
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    # Todos os parâmetros após * devem ser chamados de forma nomeada, para ficarem explícitos na função.
    # Ou seja mock_db_time(model=User). Os parâmetros não podem ser chamados de forma posicional _mock_db_time(User), isso acarretará em um erro.
    def fake_time_handler(mapper, connection, target):  # Função para alterar alterar o método created_at do objeto de target.
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)  # event.listen adiciona um evento relação a um model que será passado a função.
    # Esse evento é o before_insert, ele executará uma função (hook) antes de inserir o registro no banco de dados. O hook é a função fake_time_hook.

    yield time  # Retorna o datetime na abertura do gerenciamento de contexto.

    event.remove(model, 'before_insert', fake_time_handler)  # Após o final do gerenciamento de contexto o hook dos eventos é removido.


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session):
    user = User(username='Teste', email='teste@test.com', password='testtest')
    # Adiciona um usuário de teste ao banco de dados em memória.
    session.add(user)
    session.commit()
    session.refresh(user)

    return user
