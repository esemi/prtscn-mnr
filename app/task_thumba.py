import logging
import uuid

import requests

from settings import DST_URL_TEMPLATE, THUMBA_HOST, THUMBA_QUERY_LIMIT, USER_AGENT

if __name__ == '__main__':
    for i in range(THUMBA_QUERY_LIMIT):
        url = DST_URL_TEMPLATE % (uuid.uuid4().hex, 'thumba')
        try:
            resp = requests.post(THUMBA_HOST, params={'url': url}, headers={'User-Agent': USER_AGENT})
        except Exception as e:
            logging.info('exception %s', e)
        else:
            logging.info('%s: %s %s', i, url, resp.status_code)
