from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.models import table_registry


@pytest.fixture  # Fixture do pytest que cria um cliente de teste para a aplicação FastAPI.
def client():
    return TestClient(app)


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


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
