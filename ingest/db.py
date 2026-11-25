import os

import psycopg
from pgvector.psycopg import register_vector

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://joblens:joblens_dev@localhost:5432/joblens"
)


def get_conn():
    conn = psycopg.connect(DATABASE_URL)
    register_vector(conn)
    return conn
