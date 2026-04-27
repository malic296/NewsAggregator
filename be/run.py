from contextlib import asynccontextmanager

from elasticsearch import Elasticsearch
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from api.api.v1 import v1_router
from api.api.dependencies import generate_unique_endpoint_id
from api.core.container import ServiceContainer
from api.repositories import ArticleRepository, ChannelRepository, ConsumerRepository, LoggingRepository
from api.services import CacheService, SecurityService, EmailService, ArticleService, ChannelService, ConsumerService
from api.core.settings import Settings
from api.core.middlewares import manage_request
from api.handlers.exception_handlers import internal_exception_handler, http_exception_handler, unexpected_exception_handler
from api.core.database import create_connection_pool, create_elastic_search_client, create_valkey_client
from api.core.logger.handlers import DatabaseHandler, DropOnFailHandler
import logging
from api.core.errors import AppError
from api.core.logger import setup_logging

setup_logging()
settings = Settings()

@asynccontextmanager
async def lifespan(api: FastAPI):
    # UTILS
    db_pool = create_connection_pool(settings)
    valkey_client = create_valkey_client(settings)
    elastic_search_client = create_elastic_search_client(settings)

    # REPOSITORIES
    article_repository = ArticleRepository(connection_pool=db_pool)
    channel_repository = ChannelRepository(connection_pool=db_pool)
    consumer_repository = ConsumerRepository(connection_pool=db_pool)
    logging_repository = LoggingRepository(connection_pool=db_pool)

    # UTIL SERVICES
    cache = CacheService(client=valkey_client)
    security = SecurityService(pepper=settings.pepper, jwt=settings.jwt_secret)
    email = EmailService(resend_key=settings.resend_key)

    # CORE SERVICES
    article_service = ArticleService(articles=article_repository, cache=cache, es_client=elastic_search_client)
    channel_service = ChannelService(channels=channel_repository, cache=cache, scraping_service=None)
    consumer_service = ConsumerService(
        consumers=consumer_repository,
        cache=cache,
        security=security,
        email=email,
    )

    # LOGGER
    db_handler = DatabaseHandler(writer_func=logging_repository.log_to_db)
    db_wrapper = DropOnFailHandler(db_handler)
    logging.getLogger().addHandler(db_wrapper)

    logging.getLogger(__name__).info("API started.")

    # DEPENDENCY CONTAINER
    api.state.services = ServiceContainer(
        article_service=article_service,
        channel_service=channel_service,
        consumer_service=consumer_service,
        cache_service=cache,
        email_service=email,
        security_service=security
    )

    yield

    # FREE RESOURCES
    db_pool.close()

# APP
api = FastAPI(debug=(settings.config.environment == "dev"), generate_unique_id_function=generate_unique_endpoint_id, lifespan=lifespan)

# MIDDLEWARES
#api.add_middleware(HTTPSRedirectMiddleware)
api.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "be", "nginx"])
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.config.environment == "dev" else ["https://production.com", "localhost"],
    allow_methods=["GET", "POST"]
)

@api.middleware("http")
async def manage_request_middleware(request: Request, call_next):
    return await manage_request(request, call_next)

# EXCEPTION HANDLERS
api.add_exception_handler(Exception, unexpected_exception_handler)
api.add_exception_handler(AppError, internal_exception_handler)
api.add_exception_handler(HTTPException, http_exception_handler)

# ROUTERS
api.include_router(v1_router)
