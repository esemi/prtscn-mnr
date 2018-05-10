import logging
import uuid

import requests

from app.settings import DST_URL_TEMPLATE, MINER_KEYS, THUMBA_HOST, THUMBA_QUERY_LIMIT

if __name__ == '__main__':
    for i in range(THUMBA_QUERY_LIMIT):
        try:
            resp = requests.post(THUMBA_HOST, params={
                'url': DST_URL_TEMPLATE % (uuid.uuid4().hex, MINER_KEYS['thumba_dummy'])})
        except Exception as e:
            logging.info('exception %s', e)
        else:
            logging.info('%s: %s', i, resp.status_code)
