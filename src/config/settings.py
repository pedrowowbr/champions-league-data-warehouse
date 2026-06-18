from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuracoes centralizadas do projeto.
    O Pydantic carrega automaticamente os valores do arquivo .env
    e valida seus tipos durante a inicializacao da aplicacao.
    Caso alguma variavel obrigatoria esteja ausente,
    o erro sera exibido na inicializacao e nao durante a execucao.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Football
    api_football_key: str = Field(..., description="API Football key")
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
        """   Monta a URL de conexao com o banco de dados.
        Centralizar esta logica evita duplicacao de codigo
        e facilita futuras manutencoes."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


# Instancia unica compartilhada por todo o projeto. Segue o padrao Singleton para evitar recriacao desnecessaria.
settings = Settings()
