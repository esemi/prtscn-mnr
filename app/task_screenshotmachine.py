import logging
import uuid
import asyncio

import aiohttp

from settings import DST_URL_TEMPLATE, SCREENSHOTMACHINE_QUERY_LIMIT, SCREENSHOTMACHINE_HOST, USER_AGENT, \
    SCREENSHOTMACHINE_CONCURRENCY


async def task(num, sem: asyncio.Semaphore):
    url = DST_URL_TEMPLATE % (uuid.uuid4().hex, 'screenshotmachine')
    async with sem:
        async with aiohttp.ClientSession(headers={'User-Agent': USER_AGENT}, raise_for_status=True) as session:
            try:
                async with session.post(SCREENSHOTMACHINE_HOST, data={'urlparam': url, 'device': 'desktop'}) as response:
                    resp = await response.text()
                    logging.info('%s: %s %s', num, url, resp[:100])
            except Exception as e:
                logging.info('exception %s', e)


async def main():
    sem = asyncio.Semaphore(SCREENSHOTMACHINE_CONCURRENCY)
    tasks = [asyncio.ensure_future(task(i, sem)) for i in range(SCREENSHOTMACHINE_QUERY_LIMIT)]
    await asyncio.wait(tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
