import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from src.config.settings import settings

logger = logging.getLogger(__name__)


# Engine é caro de criar — criamos uma vez e reutilizamos (connection pool)
engine = create_engine(
    settings.database_url,
    pool_size=5,           # conexões mantidas abertas
    max_overflow=10,       # conexões extras em pico de demanda
    pool_pre_ping=True,    # testa a conexão antes de usar (evita conexões mortas)
    echo=False,            # True para ver o SQL gerado (útil em debug)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager para sessões do banco.
    Garante que a sessão é sempre fechada, mesmo em caso de erro.

    Uso:
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
    """Verifica se a conexão com o banco está funcionando."""
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))
        logger.info("Conexão com o banco estabelecida com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Falha na conexão com o banco: {e}")
        return False