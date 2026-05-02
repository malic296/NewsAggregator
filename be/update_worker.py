import asyncio
import logging
import os

from update import main


logger = logging.getLogger(__name__)
DEFAULT_INTERVAL_SECONDS = 30 * 60


async def run_forever() -> None:
    interval_seconds = int(os.getenv("UPDATE_WORKER_INTERVAL_SECONDS", DEFAULT_INTERVAL_SECONDS))

    while True:
        await main()
        logger.info("Next update scheduled in %s seconds.", interval_seconds)
        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    asyncio.run(run_forever())
