#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import uuid

import requests
from pyppeteer import launch

from settings import DEFAULT_TIMEOUT, CBT_CRED_FILE, DST_URL_TEMPLATE

BROWSER = None
DEBUG = True
LIMIT_TASKS = 5
PASS = 'qwerty12456789qwerty'
LOGIN_MASK = '%s@gmail.com'
# todo proxy


class XBT:
    endpoint_template = 'https://crossbrowsertesting.com/api/v3/%s'

    def __init__(self, user, pswd):
        self.user = user
        self.pswd = pswd

    def browsers_list(self) -> list:
        url = self.endpoint_template % 'screenshots/browsers'
        response = requests.get(url, auth=(self.user, self.pswd))
        response.raise_for_status()
        return response.json()

    def get_screenshots(self) -> dict:
        url = self.endpoint_template % 'screenshots/'
        response = requests.get(url, auth=(self.user, self.pswd), params={'archived': 'false'})
        response.raise_for_status()
        return response.json()

    def create_task(self, url) -> bool:
        pass

    def rerun_task(self, id, version) -> bool:
        url = self.endpoint_template % ('screenshots/%s/%s' % (id, version))
        response = requests.post(url, auth=(self.user, self.pswd), params={'archived': 'false'})
        response.raise_for_status()
        print(response.json())


async def upsert_and_run(user: str, pswd: str):
    logging.info('start upsert run tasks %s:%s', user, pswd)
    client = XBT(user, pswd)
    tasks = client.get_screenshots()
    logging.info('found %d tasks', tasks['meta']['record_count'])
    if tasks['meta']['record_count'] < LIMIT_TASKS:
        for i in range(LIMIT_TASKS - tasks['meta']['record_count']):
            logging.info('create task')
            url = DST_URL_TEMPLATE % ('www', uuid.uuid4().hex, 'cbt')
            client.create_task(url)
        tasks = client.get_screenshots()

    # rerun not active tasks
    logging.info('rerun tasks')
    for task in tasks['screenshots']:
        if task['active']:
            logging.info('task already active %s', task['screenshot_test_id'])
            continue

        logging.info('rerun task %s', task['screenshot_test_id'])

        print(task)
        sdsds



async def main():
    need_reg_new = False
    user = pswd = None
    try:
        with open(CBT_CRED_FILE, 'r') as f:
            user, pswd = f.readlines()[0].split(':')
    except Exception:
        need_reg_new = True
    else:
        res = await upsert_and_run(user, pswd)
        if not res:
            need_reg_new = True

    sdsdsd

    if need_reg_new:
        user, pswd = await register_new_acc()
        # save creds to file
        with open(CBT_CRED_FILE, 'x') as f:
            f.write('%s:%s' % (user, pswd))

        await upsert_and_run(user, pswd)

    try:
        await asyncio.sleep(250)
        await BROWSER.close()
    except:
        pass


async def register_new_acc():
    global BROWSER

    login = LOGIN_MASK % uuid.uuid4().hex
    logging.info('start registration %s', login)
    BROWSER = await launch(headless=not DEBUG, ignoreHTTPSErrors=False,
                           executablePath='/usr/bin/google-chrome-stable')

    page = await BROWSER.newPage()
    await page.goto('https://crossbrowsertesting.com/freetrial', timeout=DEFAULT_TIMEOUT * 1000)
    email_elem = await page.waitForSelector('.email input', timeout=DEFAULT_TIMEOUT * 1000)
    pass_elem = await page.waitForSelector('.password input', timeout=DEFAULT_TIMEOUT * 1000)
    submit_elem = await page.waitForSelector('.submit-btn', timeout=DEFAULT_TIMEOUT * 1000)
    await email_elem.type(login, {'delay': 59})
    await pass_elem.type(PASS, {'delay': 59})
    await submit_elem.click()

    await page.waitForSelector('a.utility-nav-item-link', timeout=DEFAULT_TIMEOUT * 1000)
    logging.info('complete registration %s', login)
    return login, PASS


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(main())
    ioloop.close()
