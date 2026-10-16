import os
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool


def _database_uri():
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        for prefixo in ("postgresql://", "postgres://"):
            if url.startswith(prefixo):
                url = "postgresql+psycopg://" + url[len(prefixo):]
        if "supabase" in url and "sslmode" not in url:
            url += ("&" if "?" in url else "?") + "sslmode=require"
        return url
    senha = os.getenv("DB_PASSWORD")
    if not senha:
        raise RuntimeError("Defina DATABASE_URL ou DB_PASSWORD (veja .env.example).")
    return URL.create(
        "postgresql+psycopg", username=os.getenv("DB_USERNAME", "postgres"), password=senha,
        host=os.getenv("DB_HOST", "localhost"), port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "thayane_db"), query={"sslmode": os.getenv("DB_SSLMODE", "prefer")})


class Config:
    DEBUG_MODE = os.getenv("FLASK_DEBUG") == "1"
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    if str(SQLALCHEMY_DATABASE_URI).startswith("postgresql"):
        # prepare_threshold=None: compatível com o pooler (pgbouncer) do Supabase.
        SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"prepare_threshold": None}, "pool_pre_ping": True}
        if os.getenv("VERCEL"):  # serverless: sem pool local; o pooler do Supabase gerencia as conexões
            SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"prepare_threshold": None}, "poolclass": NullPool}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = not DEBUG_MODE
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8
    MAX_CONTENT_LENGTH = 256 * 1024
    MAIL_HOST = os.getenv("MAIL_HOST", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DESTINO = os.getenv("MAIL_DESTINO", "alcantarathayaneluize@gmail.com")
