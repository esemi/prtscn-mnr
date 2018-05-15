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
from faker import Faker

from settings import DEFAULT_TIMEOUT, DST_URL_TEMPLATE, USER_AGENT, get_proxy

CBT_CRED_FILE = os.path.expanduser('~/cbt_cred.json')
BROWSER = None
LIMIT_TASKS = 5
PASS = 'qwerty12456789qwerty'


class XBT:
    endpoint_template = 'https://crossbrowsertesting.com/api/v3/%s'

    def __init__(self, user, pswd, proxy):
        self.user = user
        self.pswd = pswd
        self.proxy = proxy

    def _get(self, url, params={}):
        proxies = {'http': 'http://%s' % self.proxy,'https': 'http://%s' % self.proxy}
        return requests.get(url, verify=False, auth=(self.user, self.pswd), proxies=proxies, params=params)

    def _post(self, url, params={}):
        proxies = {'http': 'http://%s' % self.proxy,'https': 'http://%s' % self.proxy}
        return requests.post(url, verify=False, auth=(self.user, self.pswd), proxies=proxies, params=params)

    def browsers_list(self) -> list:
        url = self.endpoint_template % 'screenshots/browsers'
        response = self._get(url)
        response.raise_for_status()
        d = response.json()
        browsers = list(set([j['api_name'] for i in d
                             for j in i['browsers'] if j['device'] == 'desktop' and j['major_browser']]))
        random.shuffle(browsers)
        return browsers

    def get_screenshots(self, inactive_only=False) -> dict:
        url = self.endpoint_template % 'screenshots/'
        params = {'archived': 'false'}
        response = self._get(url, params)
        response.raise_for_status()
        d = response.json()

        if inactive_only:
            out = copy.copy(d)
            out['screenshots'] = []
            for i in d['screenshots']:
                active_versions = [j for j in i['versions'] if j['active']]
                if not len(active_versions):
                    out['screenshots'].append(i)
            return out
        else:
            return d

    def create_task(self, dst, browsers: list) -> Optional[int]:
        url = self.endpoint_template % 'screenshots/'
        response = self._post(url, {'url': dst, 'delay': 60, 'browsers': browsers[:25]})
        try:
            return response.json()['screenshot_test_id']
        except:
            logging.warning('create task exception %s', response.content)
            return None

    def rerun_task(self, id, version) -> bool:
        url = self.endpoint_template % ('screenshots/%s/%s' % (id, version))
        response = self._post(url, {'screenshot_test_id': id, 'version_id': version})
        try:
            id = response.json()['screenshot_test_id']
            return True
        except:
            logging.warning('rerun task exception %s', response.content)
            return False


def get_random_email():
    locale = random.choice(['fr_FR', 'it_IT', 'en_AU', 'en_CA', 'en_GB', 'en_US', 'es_ES'])
    fake = Faker(locale)
    name = fake.name().strip().lower().replace(' ', '_')
    domain = random.choice(['gmail.com', 'hotmail.com', 'outlook.com.au'])
    return '%s%s@%s' % (name, random.randint(74, 2018), domain)


async def upsert_and_run_tasks(user: str, pswd: str, proxy: str) -> bool:
    logging.info('start upsert run tasks %s:%s', user, pswd)
    client = XBT(user, pswd, proxy)
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

    l = len(client.get_screenshots(True)['screenshots'])
    logging.info('result not active tasks %s', l)
    return l < LIMIT_TASKS


async def main():
    proxy = get_proxy()
    need_reg_new = False
    user = pswd = None
    try:
        with open(CBT_CRED_FILE, 'r') as f:
            user, pswd = f.readlines()[0].split(':')
    except Exception:
        need_reg_new = True
    else:
        res = await upsert_and_run_tasks(user, pswd, proxy)
        if not res:
            need_reg_new = True

    if need_reg_new:
        try:
            os.remove(CBT_CRED_FILE)
        except:
            pass

        user, pswd = await register_new_acc(proxy)
        # save creds to file
        with open(CBT_CRED_FILE, 'w') as f:
            f.write('%s:%s' % (user, pswd))

        await upsert_and_run_tasks(user, pswd, proxy)

    try:
        await asyncio.sleep(10)
        await BROWSER.close()
    except:
        pass


async def register_new_acc(proxy: str):
    global BROWSER

    login = get_random_email()
    logging.info('start registration %s:%s', login, PASS)
    BROWSER = await launch(headless=False, ignoreHTTPSErrors=False,
                           executablePath='/usr/bin/google-chrome-stable', args=['--proxy-server=%s' % proxy])

    page = await BROWSER.newPage()
    await page.setUserAgent(USER_AGENT)
    await page.goto('https://crossbrowsertesting.com/freetrial', timeout=DEFAULT_TIMEOUT * 1000)
    email_elem = await page.waitForSelector('.email input', timeout=DEFAULT_TIMEOUT * 1000)
    await email_elem.type(login, {'delay': 59})

    pass_elem = await page.waitForSelector('.password input', timeout=DEFAULT_TIMEOUT * 1000)
    await pass_elem.type(PASS, {'delay': 59})

    submit_elem = await page.waitForSelector('.submit-btn', timeout=DEFAULT_TIMEOUT * 1000)
    await submit_elem.hover()
    await submit_elem.click()

    await page.waitForSelector('a.utility-nav-item-link', timeout=DEFAULT_TIMEOUT * 1000)
    logging.info('complete registration %s', login)
    return login, PASS


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(main())
    ioloop.close()
