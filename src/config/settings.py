from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Configurações centralizadas do projeto.
    Pydantic lê automaticamente do .env e valida os tipos.
    Se uma variável obrigatória estiver faltando, o erro aparece
    na inicialização — não no meio da execução.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Football
    api_football_key: str = Field(..., description="Chave da API Football")
    api_football_base_url: str = Field(
        default="https://v3.football.api-sports.io"
    )

    # PostgreSQL
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)

    @property
    def database_url(self) -> str:
        """Monta a URL de conexão de forma segura, sem expor senha em logs."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


# Instância única compartilhada por todo o projeto (Singleton pattern)
settings = Settings()