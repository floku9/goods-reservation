from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # noqa

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class BackendSettings(BaseSettings):
    BACKEND_HOST: str
    BACKEND_PORT: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


db_settings = DBSettings()
backend_settings = BackendSettings()
