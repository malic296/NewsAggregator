from psycopg_pool import ConnectionPool
from elasticsearch import Elasticsearch
from redis import Redis
from .errors import DependencyUnavailableError
from .settings import Settings
from redis.retry import Retry
from redis.backoff import NoBackoff

def create_connection_pool(settings: Settings) -> ConnectionPool:
    try:
        conn_string = f"{settings.db_server}://{settings.db_user}:{settings.db_password}@{settings.db_address}:{settings.db_port}/{settings.db_name}"

        return ConnectionPool(
            conn_string,
            timeout=1.0,
            open=True
        )
    except Exception as e:
        raise DependencyUnavailableError(dependency="PostgreSQL")


def create_elastic_search_client(settings: Settings):
    try:
        client = Elasticsearch(settings.elastic_search_conn)
        client.ping()
        return client
    except Exception as e:
        raise DependencyUnavailableError(dependency="ElasticSearch")


def create_valkey_client(settings: Settings) -> Redis:
    try:
        client = Redis(
            host=settings.valkey_host,
            port=settings.valkey_port,
            db=settings.valkey_db,
            decode_responses=True,
            retry=Retry(NoBackoff(), 0),
            socket_connect_timeout=2.0
        )

        client.ping()
        return client
    except Exception as e:
        raise DependencyUnavailableError(dependency="VALKEY")

