#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from ruamel import yaml
from doit.task import clean_targets
from utils.fmt import fmt
from utils.shell import call, rglob, globs, which

import pkg_resources

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
BRANCHES = fmt('{REPONAME}/branches')

REPOURL = 'https://github.com/mozilla/planet-content'
REVISION = os.environ.get('PLANET_CONTENT_REVISION', 'master')

REQS = [
    'git',
    'pip',
]

def is_cloned():
    '''
    check if repo is cloned
    '''
    if os.path.isdir(REPONAME):
        return 0 == call(fmt('cd {REPONAME} && git rev-parse --is-inside-work-tree'))[0]
    return False

def check_hash(program):
    from subprocess import check_call, CalledProcessError, PIPE
    try:
        check_call(fmt('hash {program}'), shell=True, stdout=PIPE, stderr=PIPE)
        return True
    except CalledProcessError:
        return False

def get_inis():
    '''
    get all of the config.ini files
    '''
    return [branch + '/config.ini' for branch in os.listdir(BRANCHES)]

def pip_reqs_met():
    requirements = open('requirements.txt').read().split('\n')
    try:
        pkg_resources.require(requirements)
    except Exception as ex:
        print(ex)
        return False
    return True

def task_reqs():
    '''
    check for required software
    '''
    for req in REQS:
        yield dict(
            name='check-hash-'+req,
            actions=[(check_hash, (req,))],
        )
    yield dict(
        name='requirements.txt',
        actions=['pip install -r requirements.txt'],
        uptodate=[pip_reqs_met],
    )

def task_clone():
    '''
    clone the planet-content repo
    '''
    return dict(
        task_dep=['reqs'],
        actions=[
            fmt('git clone {REPOURL}'),
       ],
       uptodate=[is_cloned],
    )

def task_checkout():
    '''
    checkout the correct revision
    '''
    return dict(
        task_dep=['clone'],
        actions=[
            fmt('cd {REPONAME} && git checkout {REVISION}'),
        ],
    )

def task_test():
    '''
    running pytest
    '''
    for ini in get_inis():
        yield dict(
            task_dep=['checkout'],
            name=ini,
            actions=[fmt('echo {ini}')],
        )

def task_tidy():
    '''
    clean repo
    '''
    return dict(
        actions=['git clean -xfd'],
    )
