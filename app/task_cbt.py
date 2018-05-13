#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import random
import uuid
from typing import Optional
import copy

import os
import requests
from pyppeteer import launch

from settings import DEFAULT_TIMEOUT, DST_URL_TEMPLATE


CBT_CRED_FILE = os.path.expanduser('~/cbt_cred.json')
BROWSER = None
DEBUG = False
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
        d = response.json()
        browsers = list(set([j['api_name'] for i in d
                             for j in i['browsers'] if j['device'] == 'desktop' and j['major_browser']]))
        random.shuffle(browsers)
        return browsers

    def get_screenshots(self, inactive_only=False) -> dict:
        url = self.endpoint_template % 'screenshots/'
        params = {'archived': 'false'}
        response = requests.get(url, auth=(self.user, self.pswd), params=params)
        response.raise_for_status()
        d = response.json()

        if inactive_only:
            out = copy.copy(d)
            out['screenshots'] = []
            for i in d['screenshots']:
                active_versions = [j for j in i['versions'] if j['active']]
                if not active_versions:
                    out['screenshots'].append(i)
            return out
        else:
            return d

    def create_task(self, dst, browsers: list) -> Optional[int]:
        url = self.endpoint_template % 'screenshots/'
        response = requests.post(url, auth=(self.user, self.pswd), params={
            'url': dst, 'delay': 60, 'browsers': browsers[:25]
        })
        try:
            return response.json()['screenshot_test_id']
        except:
            logging.warning('create task exception %s', response.content)
            return None

    def rerun_task(self, id, version) -> bool:
        url = self.endpoint_template % ('screenshots/%s/%s' % (id, version))
        response = requests.post(url, auth=(self.user, self.pswd), params={'screenshot_test_id': id,
                                                                           'version_id': version})
        try:
            id = response.json()['screenshot_test_id']
            return True
        except:
            logging.warning('rerun task exception %s', response.content)
            return False


async def upsert_and_run_tasks(user: str, pswd: str) -> bool:
    logging.info('start upsert run tasks %s:%s', user, pswd)
    client = XBT(user, pswd)
    tasks = client.get_screenshots()
    logging.info('found %d tasks', tasks['meta']['record_count'])
    if tasks['meta']['record_count'] < LIMIT_TASKS:
        browser_names = client.browsers_list()
        for i in range(LIMIT_TASKS - tasks['meta']['record_count']):
            logging.info('create task')
            url = DST_URL_TEMPLATE % ('www', uuid.uuid4().hex, 'cbt')
            res = client.create_task(url, browser_names)
            logging.info('create task result %s', res)

    # rerun not active tasks
    tasks = client.get_screenshots(True)
    logging.info('rerun not active tasks %d', len(tasks['screenshots']))
    for task in tasks['screenshots']:
        logging.info('rerun task %s %s', task['screenshot_test_id'], task['versions'][0]['version_id'])
        res = client.rerun_task(task['screenshot_test_id'], task['versions'][0]['version_id'])
        logging.info('rerun task result %s', res)

    return len(client.get_screenshots(True)) < LIMIT_TASKS


async def main():
    need_reg_new = False
    user = pswd = None
    try:
        with open(CBT_CRED_FILE, 'r') as f:
            user, pswd = f.readlines()[0].split(':')
    except Exception:
        need_reg_new = True
    else:
        res = await upsert_and_run_tasks(user, pswd)
        if not res:
            need_reg_new = True

    if need_reg_new:
        user, pswd = await register_new_acc()
        # save creds to file
        with open(CBT_CRED_FILE, 'x') as f:
            f.write('%s:%s' % (user, pswd))

        await upsert_and_run_tasks(user, pswd)

    try:
        await asyncio.sleep(10)
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
