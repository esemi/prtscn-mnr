#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from fabric.api import env, run, put
from fabric.contrib.files import exists

env.user = 'utils'

REMOTE_PATH = os.path.join('/home', env.user)
LOCAL_PATH = os.path.join(os.path.dirname(__file__), 'www')


def tests():
    pass


def deploy():
    if not exists(REMOTE_PATH):
        run('mkdir -p %s' % REMOTE_PATH)
    put(LOCAL_PATH, REMOTE_PATH)
    run('chgrp -R www-data %s' % REMOTE_PATH)
