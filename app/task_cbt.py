#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import uuid

from pyppeteer import launch

TIMEOUT = 45
BROWSER = None
DEBUG = True
PASS = 'qwerty12456789qwerty'
LOGIN_MASK = '%s@gmail.com'


async def main():
    # fetch creds from file
    # check creds limit
    cred_valid = False
    if not cred_valid:
        user, pswd = await register_new_acc()
        # save creds to file


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
    await page.goto('https://crossbrowsertesting.com/freetrial', timeout=TIMEOUT * 1000)
    email_elem = await page.waitForSelector('.email input', timeout=TIMEOUT * 1000)
    pass_elem = await page.waitForSelector('.password input', timeout=TIMEOUT * 1000)
    submit_elem = await page.waitForSelector('.submit-btn', timeout=TIMEOUT * 1000)
    await email_elem.type(login, {'delay': 59})
    await pass_elem.type(PASS, {'delay': 59})
    await submit_elem.click()

    menu_elem = await page.waitForSelector('a.utility-nav-item-link', timeout=TIMEOUT * 1000)
    await menu_elem.click()
    logging.info('complete registration %s', login)
    return login, PASS


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(register_new_acc())
    ioloop.close()
