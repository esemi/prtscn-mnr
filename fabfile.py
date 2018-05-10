#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from fabric.api import env, run, put, cd, lcd
from fabric.contrib.files import exists
from fabric.operations import local
from shutil import rmtree, copytree

env.user = 'prtscnmnr'

BUILD_FILENAME = 'build.tar.gz'
BUILD_FOLDERS = ['app', 'www', 'conf']
LOCAL_APP_PATH = os.path.dirname(__file__)
LOCAL_BUILD_PATH = os.path.join(LOCAL_APP_PATH, 'build')
LOCAL_BUILD_BUNDLE = os.path.join(LOCAL_APP_PATH, BUILD_FILENAME)

REMOTE_HOME_PATH = os.path.join('/home', env.user)
APP_PATH = os.path.join(REMOTE_HOME_PATH, 'current')
DEPLOY_PATH = os.path.join(REMOTE_HOME_PATH, 'deploy')
BACKUP_PATH = os.path.join(REMOTE_HOME_PATH, 'backup')
VENV_PATH = os.path.join(REMOTE_HOME_PATH, 'venv')
LOG_PATH = os.path.join(REMOTE_HOME_PATH, 'logs')


def tests():
    pass


def deploy():
    # init remote host
    if not exists(APP_PATH):
        run('mkdir -p %s' % APP_PATH)
    if not exists(VENV_PATH):
        with cd(REMOTE_HOME_PATH):
            run('python3.6 -m venv %s' % VENV_PATH)
            run('%s/bin/pip install --upgrade pip' % VENV_PATH)
    if not exists(LOG_PATH):
        run('mkdir -p %s' % LOG_PATH)

    # make local build
    if os.path.exists(LOCAL_BUILD_PATH):
        rmtree(LOCAL_BUILD_PATH)
    os.mkdir(LOCAL_BUILD_PATH)
    for folder in BUILD_FOLDERS:
        copytree(os.path.join(LOCAL_APP_PATH, folder), os.path.join(LOCAL_BUILD_PATH, folder))
    with lcd(LOCAL_BUILD_PATH):
        local('find . -name \*.pyc -delete')
        local('tar -czf %s .' % LOCAL_BUILD_BUNDLE)
    rmtree(LOCAL_BUILD_PATH)

    # load build
    if exists(DEPLOY_PATH):
        run('rm -rf %s' % DEPLOY_PATH)
    run('mkdir -p %s' % DEPLOY_PATH)
    put(LOCAL_BUILD_BUNDLE, DEPLOY_PATH)

    with cd(DEPLOY_PATH):
        run('tar -xzf %s' % BUILD_FILENAME)
        run('%s/bin/pip install -r conf/requirements.txt' % VENV_PATH)
        run('crontab conf/crontab.txt')

    # deploy (move build to production)
    run('chgrp -R www-data %s' % DEPLOY_PATH)
    if exists(BACKUP_PATH):
        run('rm -rf %s' % BACKUP_PATH)
    run('mv %s %s' % (APP_PATH, BACKUP_PATH))
    run('mv %s %s' % (DEPLOY_PATH, APP_PATH))



