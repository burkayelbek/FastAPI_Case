from os import getenv
from sqlalchemy import create_engine

DATABASE_BASE_URL = "postgresql+psycopg2://"


class Settings:
    SECRET_KEY: str = getenv("SECRET_KEY")

    def postgresql_database_connection(self) -> object:

        engine = create_engine(
            "{BASE_URL}{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}".format(
                BASE_URL=DATABASE_BASE_URL,
                POSTGRES_USER=getenv("POSTGRES_USER"),
                POSTGRES_PASSWORD=getenv("POSTGRES_PASSWORD"),
                POSTGRES_HOST=getenv("POSTGRES_HOST"),
                POSTGRES_PORT=getenv("POSTGRES_PORT"),
                POSTGRES_DB=getenv("POSTGRES_DB")
            )
        )

        return engine


settings = Settings()
