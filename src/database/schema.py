from sqlalchemy import text
from src.database.connection import get_db_session
import logging

logger = logging.getLogger(__name__)


BRONZE_SCHEMA = """
-- Esquema Bronze: dados brutos da API, sem transformacao

CREATE SCHEMA IF NOT EXISTS bronze;

-- Partidas (fixtures) da Champions League
CREATE TABLE IF NOT EXISTS bronze.fixtures (
    id              SERIAL PRIMARY KEY,
    fixture_id      INTEGER NOT NULL UNIQUE,
    raw_data        JSONB NOT NULL,
    extracted_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Estatisticas por partida
CREATE TABLE IF NOT EXISTS bronze.fixture_stats (
    id              SERIAL PRIMARY KEY,
    fixture_id      INTEGER NOT NULL UNIQUE,
    raw_data        JSONB NOT NULL,
    extracted_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Classificacao da fase de grupos
CREATE TABLE IF NOT EXISTS bronze.standings (
    id              SERIAL PRIMARY KEY,
    season          INTEGER NOT NULL,
    raw_data        JSONB NOT NULL,
    extracted_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Artilheiros da temporada
CREATE TABLE IF NOT EXISTS bronze.top_scorers (
    id              SERIAL PRIMARY KEY,
    season          INTEGER NOT NULL,
    raw_data        JSONB NOT NULL,
    extracted_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Estatisticas individuais de jogadores
CREATE TABLE IF NOT EXISTS bronze.player_stats (
    id              SERIAL PRIMARY KEY,
    player_id       INTEGER NOT NULL,
    season          INTEGER NOT NULL,
    raw_data        JSONB NOT NULL,
    extracted_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (player_id, season)
);

-- Indices para busca rapida por fixture_id
CREATE INDEX IF NOT EXISTS idx_bronze_fixtures_fixture_id
    ON bronze.fixtures(fixture_id);

CREATE INDEX IF NOT EXISTS idx_bronze_fixture_stats_fixture_id
    ON bronze.fixture_stats(fixture_id);
"""


def criar_schemas() -> None:
    """Cria todos os schemas e tabelas Bronze no banco."""
    try:
        with get_db_session() as session:
            session.execute(text(BRONZE_SCHEMA))
        logger.info("Schemas Bronze criados com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao criar schemas: {e!r}")
        raise
