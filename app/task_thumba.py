import logging
import uuid

import requests

from settings import DST_URL_TEMPLATE, USER_AGENT, DEFAULT_TIMEOUT, get_proxy

THUMBA_HOST = 'https://www.thumbalizr.com/demo'
THUMBA_QUERY_LIMIT = 50


if __name__ == '__main__':
    logging.info('start')
    proxy = get_proxy()

    for i in range(THUMBA_QUERY_LIMIT):
        url = DST_URL_TEMPLATE % ('www', uuid.uuid4().hex, 'thumba')
        try:
            resp = requests.post(THUMBA_HOST, params={'url': url}, headers={'User-Agent': USER_AGENT},
                                 timeout=DEFAULT_TIMEOUT, verify=False, proxies={'http': 'http://%s' % proxy,
                                                                                 'https': 'http://%s' % proxy})
        except Exception as e:
            logging.info('exception %s', e)
            proxy = get_proxy()
        else:
            logging.info('%s: %s %s', i, url, resp.status_code)
            if resp.status_code not in (200, 500):
                proxy = get_proxy()

    logging.info('end')
