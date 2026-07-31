import logging
from typing import Any

from sqlalchemy import text

from src.database.connection import get_db_session
from src.extract.api_client import APIFootballClient, SEASON

logger = logging.getLogger(__name__)


class BronzeLoader:
    """
    Responsavel por extrair dados da API Football
    e gravar na camada Bronze do Data Warehouse.

    Principio: dados brutos, sem transformacao.
    Idempotente: rodar multiplas vezes nao duplica registros.
    """

    def __init__(self) -> None:
        self.client = APIFootballClient()

    def _fixture_ja_existe(self, session: Any, fixture_id: int) -> bool:
        """Verifica se uma partida ja foi extraida anteriormente."""
        resultado = session.execute(
            text("SELECT 1 FROM bronze.fixtures WHERE fixture_id = :id"),
            {"id": fixture_id},
        ).fetchone()
        return resultado is not None

    def carregar_fixtures(self) -> int:
        """
        Extrai todas as partidas e grava na tabela bronze.fixtures.
        Pula partidas que ja existem no banco (idempotencia).
        Retorna o numero de registros inseridos.
        """
        logger.info("Extraindo fixtures da Champions League 2023/24...")
        fixtures = self.client.get_fixtures()
        logger.info(f"Total de fixtures recebidos da API: {len(fixtures)}")

        inseridos = 0
        pulados = 0

        with get_db_session() as session:
            for fixture in fixtures:
                fixture_id = fixture["fixture"]["id"]

                if self._fixture_ja_existe(session, fixture_id):
                    pulados += 1
                    continue

                session.execute(
                    text("""
                        INSERT INTO bronze.fixtures (fixture_id, raw_data)
                        VALUES (:fixture_id, CAST(:raw_data AS JSONB))
                    """),
                    {
                        "fixture_id": fixture_id,
                        "raw_data": __import__("json").dumps(fixture),
                    },
                )
                inseridos += 1

        logger.info(f"Fixtures: {inseridos} inseridos, {pulados} ja existiam.")
        return inseridos

    def carregar_standings(self) -> int:
        """
        Extrai a classificacao e grava na tabela bronze.standings.
        """
        logger.info("Extraindo standings da Champions League 2023/24...")
        standings = self.client.get_standings()

        with get_db_session() as session:
            # Remove registro anterior da mesma temporada antes de inserir
            session.execute(
                text("DELETE FROM bronze.standings WHERE season = :season"),
                {"season": SEASON},
            )

            session.execute(
                text("""
                    INSERT INTO bronze.standings (season, raw_data)
                    VALUES (:season, CAST(:raw_data AS JSONB))
                """),
                {
                    "season": SEASON,
                    "raw_data": __import__("json").dumps(standings),
                },
            )

        logger.info("Standings inseridos com sucesso.")
        return 1

    def carregar_top_scorers(self) -> int:
        """
        Extrai artilheiros e grava na tabela bronze.top_scorers.
        """
        logger.info("Extraindo top scorers da Champions League 2023/24...")
        top_scorers = self.client.get_top_scorers()

        with get_db_session() as session:
            session.execute(
                text("DELETE FROM bronze.top_scorers WHERE season = :season"),
                {"season": SEASON},
            )

            session.execute(
                text("""
                    INSERT INTO bronze.top_scorers (season, raw_data)
                    VALUES (:season, CAST(:raw_data AS JSONB))
                """),
                {
                    "season": SEASON,
                    "raw_data": __import__("json").dumps(top_scorers),
                },
            )

        logger.info(f"Top scorers: {len(top_scorers)} jogadores inseridos.")
        return len(top_scorers)

    def carregar_tudo(self) -> None:
        """
        Executa a extracao completa na ordem correta.
        Fixtures primeiro — outros loaders podem depender deles futuramente.
        """
        logger.info("=== Iniciando carga Bronze ===")

        self.carregar_fixtures()
        self.carregar_standings()
        self.carregar_top_scorers()

        logger.info("=== Carga Bronze finalizada ===")
