import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Engine e custosa para criar. Criada uma unica vez e reutilizada atraves do pool de conexoes.
engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Gerenciador de contexto para sessoes do banco de dados.
    Garante que:
    - A transacao seja confirmada em caso de sucesso.
    - A transacao seja revertida em caso de erro.
    - A sessao seja sempre encerrada corretamente.
    Exemplo de uso:
    with get_db_session() as session:
    session.execute(text("SELECT 1"))
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection() -> bool:
    """Verifica se a conexao com o banco esta funcionando."""
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))
        logger.info("Conexao com o banco estabelecida com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Erro: {e!r}")
        return False
