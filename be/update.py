from httpx import AsyncClient
import asyncio
from api.core.errors import AppError
from api.core.settings import Settings
from api.core.clients import create_connection_pool, create_valkey_client, create_elastic_search_client
from api.services.channel_service import ChannelService
from api.services.scraping_service import ScrapingService
from api.services import CacheService
from api.core.logger.handlers import DropOnFailHandler, DatabaseHandler
from api.repositories import LoggingRepository, ChannelRepository, ElasticSearchRepository
import logging
from api.core.logger import setup_logging

async def main() -> None:
    setup_logging()
    settings: Settings = Settings()
    db_pool = create_connection_pool(settings)
    es_client = create_elastic_search_client(settings)
    logging_repo = LoggingRepository(connection_pool=db_pool)
    db_handler = DatabaseHandler(writer_func=logging_repo.log_to_db)
    db_wrapper = DropOnFailHandler(db_handler)
    logging.getLogger().addHandler(db_wrapper)

    logger = logging.getLogger(__name__)
    logger.info("update.py started.")

    try:
        async with AsyncClient(timeout=5.0) as client:
            scraping_service = ScrapingService(client)
            channel_service = ChannelService(
                channels=ChannelRepository(connection_pool=db_pool),
                cache=CacheService(create_valkey_client(settings)),
                scraping_service=scraping_service,
                elasticsearch=ElasticSearchRepository(es_client)
            )
            logger.info("Dependencies loaded.")

            await channel_service.update_channels(channel_urls=settings.config.feeds, hours=settings.config.update_interval)

            logger.info("Channels and articles updated.")

    except AppError as e:
        logging.getLogger(__name__).error(e.internal_message, extra={'exception': e})
    except Exception as e:
        logging.getLogger(__name__).error("UNEXPECTED ERROR: " + str(e), extra={'exception': e})
    finally:
        db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())
