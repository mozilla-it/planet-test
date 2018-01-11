#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from ruamel import yaml
from doit.task import clean_targets
from utils.fmt import fmt, pfmt
from utils.shell import call, rglob, globs, which

import requests
import pkg_resources
from bs4 import BeautifulSoup

DOIT_CONFIG = {
    'verbosity': 2,
    'default_tasks': ['post'],
}

try:
    J = call('nproc')[1].strip()
except:
    J = 1

REPOROOT = os.path.dirname(os.path.abspath(__file__))
REPONAME = 'planet-content'
REPOURL = 'https://github.com/mozilla/planet-content'
REVISION = os.environ.get('PLANET_CONTENT_REVISION', 'master')

REQS = [
    'git',
    'pip',
]

def check_hash(program):
    from subprocess import check_call, CalledProcessError, PIPE
    try:
        check_call(fmt('hash {program}'), shell=True, stdout=PIPE, stderr=PIPE)
        return True
    except CalledProcessError:
        return False

def clone(repourl, reponame):
    '''
    clone the mozilla/planet-content repo
    '''
    if os.path.isdir(reponame):
        if 0 == call(fmt('cd {reponame} && git rev-parse --is-inside-work-tree'))[0]:
            return
        call(fmt('rm -rf {reponame}'))
    call(fmt('git clone {repourl}'))

def checkout(reponame, revision):
    '''
    checkout the appropriate revision
    '''
    call(fmt('cd {reponame} && git checkout {revision}'))

def get_planets(repourl, reponame, revision):
    '''
    get all of the planets that have config.ini
    '''
    if not check_hash('git'):
        raise Exception('git missing')
    branches = fmt('{reponame}/branches/')
    clone(repourl, reponame)
    checkout(reponame, revision)
    return [planet for planet in os.listdir(branches) if os.path.isfile(branches + planet + '/config.ini')]

def requirements(filename):
    '''
    install required pkgs
    '''
    reqs = open(filename).read().split('\n')
    pkg_resources.require(reqs)

def task_reqs():
    '''
    install requirements
    '''
    return dict(
        actions=[lambda: requirements('requirements.txt')],
    )

def task_test():
    '''
    running pytest
    '''
    planets = get_planets(REPOURL, REPONAME, REVISION)
    for planet in planets:
        yield dict(
            task_dep=['reqs'],
            name=planet,
            actions=[fmt('pytest -vv -s --ini {REPONAME}/branches/{planet}/config.ini tests/')],
        )

def task_tidy():
    '''
    clean repo
    '''
    return dict(
        actions=['git clean -xfd'],
    )
