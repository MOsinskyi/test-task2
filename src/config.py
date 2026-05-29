from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    user: str = "postgres"
    password: str = "postgres"
    db: str = "todo_db"
    host: str = "localhost"
    port: str = "5432"

    @computed_field
    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisDB(BaseSettings):
    cache: int = 0
    celery: int = 1


class RedisConfig(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    db: RedisDB = RedisDB()


class AppConfig(BaseSettings):
    host: str = "localhost"
    port: int = 8000


class ThrottlingConfig(BaseSettings):
    limit: int = 10
    seconds: int = 5


class MailConfig(BaseSettings):
    username: str = "your_email@gmail.com"
    password: str = "your_app_password"
    mail_from: str = "your_email@gmail.com"
    port: int = 587
    server: str = "smtp.gmail.com"
    starttls: bool = True
    ssl_tls: bool = False
    use_credentials: bool = True


class Settings(BaseSettings):
    postgres: PostgresConfig = PostgresConfig()
    redis: RedisConfig = RedisConfig()
    app: AppConfig = AppConfig()
    throttling: ThrottlingConfig = ThrottlingConfig()
    email: MailConfig = MailConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        env_nested_delimiter="_",
        env_nested_max_split=1,
    )


settings = Settings()
