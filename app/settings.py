import logging

import os
import requests

DST_URL_TEMPLATE = "http://%s.prtscnmnr.esemi.ru/mnr.html?page=%s&user=%s"
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
DEFAULT_TIMEOUT = 45

THUMBA_HOST = 'https://www.thumbalizr.com/demo'
THUMBA_QUERY_LIMIT = 50

SCREENSHOTMACHINE_HOST = 'https://www.screenshotmachine.com/processor.php'
SCREENSHOTMACHINE_QUERY_LIMIT = 80
SCREENSHOTMACHINE_CONCURRENCY = 10

CBT_CRED_FILE = os.path.expanduser('~/cbt_cred.json')


logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)


def pubproxy():
    resp = requests.get('http://pubproxy.com/api/proxy?https=true&type=http&post=true&user_agent=true')
    resp.raise_for_status()
    return resp.json()['data'][0]['ipPort']


def gimme():
    resp = requests.get('https://gimmeproxy.com/api/getProxy?post=true&supportsHttps=true&user-agent=true&protocol=http')
    resp.raise_for_status()
    return resp.json()['data'][0]['ipPort']


def spin():
    apikey = 'huderg92x86zp8of949q2v92eq6l7l'
    resp = requests.get('https://spinproxies.com/api/v1/proxyrotate?key=%s&protocols=http' % apikey)
    resp.raise_for_status()
    data = resp.json()['data']['proxy']
    return '%s:%s' % (data['ip'], data['port'])


def getp():
    resp = requests.get('https://api.getproxylist.com/proxy?allowsUserAgentHeader=1&allowsPost=1&allowsHttps=1&protocol=http')
    resp.raise_for_status()
    data = resp.json()
    return '%s:%s' % (data['ip'], data['port'])


def get_proxy() -> str:
    def _():
        try:
            return pubproxy()
        except:
            pass
        try:
            return gimme()
        except:
            pass
        try:
            return spin()
        except:
            pass
        try:
            return getp()
        except:
            pass
    p = _()
    logging.info('get proxy %s', p)
    return p
