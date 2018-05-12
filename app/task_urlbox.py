import logging
import uuid

import requests

from settings import DST_URL_TEMPLATE, MINER_KEYS, URLBOX_QUERY_LIMIT, URLBOX_HOST, USER_AGENT

if __name__ == '__main__':
    for i in range(URLBOX_QUERY_LIMIT):
        url = DST_URL_TEMPLATE % (uuid.uuid4().hex, MINER_KEYS['thumba_dummy'])
        try:
            resp = requests.post(URLBOX_HOST, data={'urlparam': url, 'device': 'desktop'}, headers={
                'User-Agent': USER_AGENT})
        except Exception as e:
            logging.info('exception %s', e)
        else:
            logging.info('%s: %s %s', i, url, resp.status_code)
