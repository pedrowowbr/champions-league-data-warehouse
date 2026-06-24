import logging
import sys

from src.database.connection import test_connection
from src.database.schema import criar_schemas
from src.extract.api_client import test_api_connection
from src.config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Iniciando Champions League Data Warehouse...")
    logger.info(
        f"Banco de dados: {settings.postgres_db} @ {settings.postgres_host}")

    # Valida conexao com banco
    if not test_connection():
        logger.error(
            "Falha na conexao com o banco. Verifique o Docker e o .env.")
        sys.exit(1)

    # Cria tabelas se não existirem
    criar_schemas()

    # Valida conexao com a API
    if not test_api_connection():
        logger.error(
            "Falha na conexao com a API. Verifique a API_KEY no .env.")
        sys.exit(1)

    logger.info(
        "Fundacao OK. Banco e API funcionando. Pronto para extrair dados.")


# O main aqui serve principalmente para validar as configuracoes e conexoes antes de iniciar o processo de extracao.
if __name__ == "__main__":
    main()
