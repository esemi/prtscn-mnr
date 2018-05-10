import logging

DST_URL_TEMPLATE = "https://prtscnmnr.esemi.ru/mnr.html?page=%s#%s"
MINER_KEYS = {
    'thumba_dummy': 'VSWxpBVWI5jiiZ7itCoXO8e5jH0U5fzR',

}
THUMBA_HOST = 'todo'
THUMBA_QUERY_LIMIT = 100

try:
    from settings_local import *
except ImportError:
    pass

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
