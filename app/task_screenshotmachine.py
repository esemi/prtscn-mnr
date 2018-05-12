import logging
import uuid
import asyncio

import aiohttp
from async_timeout import timeout

from settings import DST_URL_TEMPLATE, SCREENSHOTMACHINE_QUERY_LIMIT, SCREENSHOTMACHINE_HOST, USER_AGENT, \
    SCREENSHOTMACHINE_CONCURRENCY, DEFAULT_TIMEOUT, get_proxy, spin


async def task(num, sem: asyncio.Semaphore, proxy: str):
    url = DST_URL_TEMPLATE % ('www', uuid.uuid4().hex, 'screenshotmachine')
    async with sem:
        try:
            async with timeout(DEFAULT_TIMEOUT) as cm:
                async with aiohttp.ClientSession(headers={'User-Agent': USER_AGENT}, raise_for_status=True,
                                                 connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                        async with session.post(SCREENSHOTMACHINE_HOST, data={'urlparam': url, 'device': 'desktop'},
                                                proxy='http://%s' % proxy, timeout=DEFAULT_TIMEOUT) as response:
                            resp = await response.text()
                            logging.info('%s: %s %s', num, url, resp[:100])
        except Exception as e:
            logging.info('exception %s %s', e, type(e))


async def main():
    proxy = get_proxy()
    sem = asyncio.Semaphore(SCREENSHOTMACHINE_CONCURRENCY)
    tasks = [asyncio.ensure_future(task(i, sem, proxy)) for i in range(SCREENSHOTMACHINE_QUERY_LIMIT)]
    await asyncio.wait(tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
