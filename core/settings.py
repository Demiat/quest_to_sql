from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    """Настройки для подключения базы данных."""

    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_echo: bool

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf8", extra="ignore")

    @property
    def db_url(self):
        return (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


class Settings(BaseSettings):
    """Совокупный класс настроек."""

    db_settings: DBSettings = DBSettings()


settings = Settings()
