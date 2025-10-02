from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


# Dependency para obter uma sessão de banco de dados sem precisar ficar repetindo o código em cada endpoint. no app.py
def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session
