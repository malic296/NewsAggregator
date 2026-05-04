from httpx import AsyncClient
import asyncio
from api.core.errors import AppError
from api.core.settings import Settings
from api.core.clients import create_connection_pool, create_elastic_search_client
from api.core.utils import load_embedding_model
from api.core.logger.handlers import DropOnFailHandler, DatabaseHandler
from api.repositories import LoggingRepository, ChannelRepository, ElasticSearchRepository, ArticleRepository
import logging
from api.core.logger import setup_logging
from api.repositories.themes_repository import ThemesRepository
from api.services import SemanticService, ScrapingService, UpdateService

async def main() -> None:
    setup_logging()
    settings: Settings = Settings()
    db_pool = create_connection_pool(settings)
    es_client = create_elastic_search_client(settings)
    logging_repo = LoggingRepository(connection_pool=db_pool)
    semantic_service = SemanticService(embedding_model=load_embedding_model())

    db_handler = DatabaseHandler(writer_func=logging_repo.log_to_db)
    db_wrapper = DropOnFailHandler(db_handler)
    logging.getLogger().addHandler(db_wrapper)

    logger = logging.getLogger(__name__)
    logger.info("update.py started.")

    try:
        async with AsyncClient(timeout=5.0) as client:
            scraping_service = ScrapingService(client)
            update_service = UpdateService(
                channels=ChannelRepository(connection_pool=db_pool),
                articles=ArticleRepository(connection_pool=db_pool),
                themes=ThemesRepository(connection_pool=db_pool),
                scraping_service=scraping_service,
                elasticsearch=ElasticSearchRepository(es_client),
                semantics = semantic_service
            )
            logger.info("Dependencies loaded.")

            await update_service.update_data(channel_urls=settings.config.feeds, hours=settings.config.update_interval)


            logger.info("Channels and articles updated.")

    except AppError as e:
        logging.getLogger(__name__).error(e.internal_message, extra={'exception': e})
    except Exception as e:
        logging.getLogger(__name__).error("UNEXPECTED ERROR: " + str(e), extra={'exception': e})
    finally:
        db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())
