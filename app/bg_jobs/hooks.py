from logging import getLogger

from saq.types import Context

from app.core.containers import AppContainer

logger = getLogger(__name__)


async def startup(ctx: Context) -> None:
    logger.info('Initiate resources at service startup')
    await AppContainer.init_resources()
    logger.info('Resources initiated')


async def shutdown(ctx: Context) -> None:
    logger.info('Shut down resources at shutdown')
    await AppContainer.tear_down()
