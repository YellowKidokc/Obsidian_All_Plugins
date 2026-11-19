"""
Configuration settings for Theophysics Ingest Engine

Uses environment variables or .env file for sensitive data.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class LocalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",
                                      extra="ignore", populate_by_name=True)


class DatabaseSettings(LocalSettings):
    """PostgreSQL database configuration"""

    host: str = Field(default="localhost", validation_alias="PG_HOST")
    port: int = Field(default=5432, validation_alias="PG_PORT")
    database: str = Field(default="theophysics", validation_alias="PG_DATABASE")
    user: str = Field(default="postgres", validation_alias="PG_USER")
    password: str = Field(default="", validation_alias="PG_PASSWORD")

    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string"""
        url = URL.create("postgresql", username=self.user, password=self.password or None,
                         host=self.host, port=self.port, database=self.database)
        return url.render_as_string(hide_password=False)



class IngestSettings(LocalSettings):
    """Ingest engine configuration"""

    # Batch processing
    batch_size: int = Field(default=100, validation_alias="INGEST_BATCH_SIZE")

    # Excel settings
    excel_max_rows: int = Field(default=100000, validation_alias="EXCEL_MAX_ROWS")
    excel_detect_headers: bool = Field(default=True, validation_alias="EXCEL_DETECT_HEADERS")

    # HTML settings
    html_parser: str = Field(default="lxml", validation_alias="HTML_PARSER")
    html_encoding: str = Field(default="auto", validation_alias="HTML_ENCODING")

    # Markdown settings
    markdown_parse_definitions: bool = Field(default=True, validation_alias="MD_PARSE_DEFINITIONS")
    markdown_extract_equations: bool = Field(default=True, validation_alias="MD_EXTRACT_EQUATIONS")

    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")



class VaultSettings(LocalSettings):
    """Obsidian vault configuration"""

    vault_path: Optional[str] = Field(default=None, validation_alias="OBSIDIAN_VAULT_PATH")
    ignore_folders: list = Field(
        default=[".obsidian", ".git", ".trash", "node_modules"],
        validation_alias="VAULT_IGNORE_FOLDERS"
    )
    definition_folder: Optional[str] = Field(default="Glossary", validation_alias="DEFINITION_FOLDER")



# Global settings instances
db_settings = DatabaseSettings()
ingest_settings = IngestSettings()
vault_settings = VaultSettings()


def get_db_url() -> str:
    """Get the database connection URL"""
    return db_settings.connection_string
