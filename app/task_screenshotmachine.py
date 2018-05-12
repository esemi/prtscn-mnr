import logging
import uuid

import requests

from settings import DST_URL_TEMPLATE, SCREENSHOTMACHINE_QUERY_LIMIT, SCREENSHOTMACHINE_HOST, USER_AGENT

if __name__ == '__main__':
    for i in range(SCREENSHOTMACHINE_QUERY_LIMIT):
        url = DST_URL_TEMPLATE % (uuid.uuid4().hex, 'screenshotmachine')
        try:
            resp = requests.post(SCREENSHOTMACHINE_HOST, data={'urlparam': url, 'device': 'desktop'}, headers={
                'User-Agent': USER_AGENT})
        except Exception as e:
            logging.info('exception %s', e)
        else:
            logging.info('%s: %s %s %s', i, url, resp.status_code, resp.text)
