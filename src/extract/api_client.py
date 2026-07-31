import logging
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config.settings import settings

logger = logging.getLogger(__name__)

# ID da Champions League na API Football
CHAMPIONS_LEAGUE_ID = 2
SEASON = 2026


class APIFootballClient:
    """
    Cliente HTTP para a API Football.
    Gerencia autenticacao, retry automatico e rate limiting.
    """

    def __init__(self) -> None:
        self.base_url = settings.api_football_base_url
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        """
        Cria uma sessao HTTP com retry automatico.
        Tenta novamente em erros 429 (rate limit) e 5xx (servidor).
        """
        session = requests.Session()

        session.headers.update({
            "x-apisports-key": settings.api_football_key,
            "Accept": "application/json",
        })

        # Retry automatico com backoff exponencial
        # Tentativas: imediata -> 1s -> 2s -> 4s
        retry_strategy = Retry(
            total=4,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        return session

    def _make_request(self, endpoint: str, params: dict) -> list[Any]:
        """
        Executa uma requisicao GET e retorna o campo 'response'.

        Sempre retorna uma lista — mesmo que vazia.
        Nunca deixa erros silenciosos: loga tudo e levanta excecao se necessario.
        """
        url = f"{self.base_url}/{endpoint}"

        logger.info(f"Requisicao: GET /{endpoint} | params: {params}")

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Verifica erros retornados pela propria API
        if data.get("errors"):
            logger.error(f"Erro da API: {data['errors']}")
            raise ValueError(f"API retornou erros: {data['errors']}")

        resultados = data.get("results", 0)
        logger.info(f"Resultados recebidos: {resultados}")

        return data.get("response", [])

    def get_fixtures(self) -> list[Any]:
        """
        Busca todas as partidas da Champions League 2023/24.
        Retorna lista com todas as fases: grupos, oitavas, quartas, semi e final.
        """
        return self._make_request(
            endpoint="fixtures",
            params={
                "league": CHAMPIONS_LEAGUE_ID,
                "season": SEASON,
            },
        )

    def get_fixture_stats(self, fixture_id: int) -> list[Any]:
        """
        Busca estatisticas detalhadas de uma partida especifica.
        Inclui: posse, chutes, escanteios, faltas, cartoes.

        Atencao: consome 1 requisicao por partida — use com cuidado
        por causa do rate limit de 100 req/dia no plano gratuito.
        """
        return self._make_request(
            endpoint="fixtures/statistics",
            params={"fixture": fixture_id},
        )

    def get_standings(self) -> list[Any]:
        """
        Busca a classificacao da fase de grupos.
        """
        return self._make_request(
            endpoint="standings",
            params={
                "league": CHAMPIONS_LEAGUE_ID,
                "season": SEASON,
            },
        )

    def get_top_scorers(self) -> list[Any]:
        """
        Busca os 20 maiores artilheiros da Champions League 2023/24.
        """
        return self._make_request(
            endpoint="players/topscorers",
            params={
                "league": CHAMPIONS_LEAGUE_ID,
                "season": SEASON,
            },
        )

    def get_player_stats(self, page: int = 1) -> list[Any]:
        """
        Busca estatisticas individuais de jogadores.
        A API pagina os resultados — page controla qual pagina buscar.
        """
        return self._make_request(
            endpoint="players",
            params={
                "league": CHAMPIONS_LEAGUE_ID,
                "season": SEASON,
                "page": page,
            },
        )


def test_api_connection() -> bool:
    """Valida que a API key esta correta e a API esta respondendo."""
    try:
        client = APIFootballClient()
        # Endpoint leve so para verificar autenticacao
        result = client._make_request("status", params={})
        logger.info(f"API conectada. Status: {result}")
        return True
    except Exception as e:
        logger.error(f"Falha na conexao com a API: {e!r}")
        return False
