import aiohttp
import asyncio
import logging
import backoff

logger = logging.getLogger(__name__)


def post_to_url(url, data, headers):
    """Post data to url

    "data": dict
    "url": str
    "header": dict
    """
    asyncio.run(_async_post_to_url(url, data, headers))


async def _async_post_to_url(url, data, headers):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        await asyncio.gather(*[
            _async_post(session=session,
                        data=data,
                        url=url,
                        headers=headers
                        )
        ])
        logger.info("completed submission to url: {url}".format(url=url))


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=5)
async def _async_post(session, data: dict, url: str, headers: dict):
    async with session.post(url,
                            json=data,
                            headers=headers) as resp:
        result = await resp.text()
        if resp.status != 201:
            logger.error("Error in posting to github")
            raise Exception("Error in posting to url: {result}".format(result=result))
        return result
