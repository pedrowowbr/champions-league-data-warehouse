import logging
import sys

from src.database.connection import test_connection
from src.config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Iniciando Champions League Data Warehouse...")
    logger.info(f"Banco de dados: {settings.postgres_db} @ {settings.postgres_host}")

    if not test_connection():
        logger.error("Não foi possível conectar ao banco. Verifique o Docker e o .env.")
        sys.exit(1)

    logger.info("Fundação OK. Pronto para a próxima etapa.")


if __name__ == "__main__":
    main()