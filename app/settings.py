import logging

MINER_KEYS = {
    'thumba_dummy': 'nA8P6IYnM3KluYUc7geYgUGObEERrGQF',
}

DST_URL_TEMPLATE = "https://prtscnmnr.esemi.ru/mnr.html?page=%s&user=%s"
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'

THUMBA_HOST = 'https://www.thumbalizr.com/demo'
THUMBA_QUERY_LIMIT = 50
SCREENSHOTMACHINE_HOST = 'https://www.screenshotmachine.com/processor.php'
SCREENSHOTMACHINE_QUERY_LIMIT = 50

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
