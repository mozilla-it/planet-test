'''
shell utilities
'''
import os
import re
import sys
import glob
import fnmatch
from subprocess import Popen, PIPE, CalledProcessError, check_output
from contextlib import contextmanager

#pylint: disable=invalid-name

def expandpath(path):
    return os.path.realpath(os.path.expanduser(path))

def inversepath(path):
    return '/'.join(['..' for _ in path.split('/')])

def which(string):
    output = check_output('which ' + string, shell=True)
    return output.decode('utf-8').strip()

@contextmanager
def cd(*args, **kwargs):
    mkdir = kwargs.pop('mkdir', True)
    verbose = kwargs.pop('verbose', False)
    path = os.path.sep.join(args)
    path = os.path.normpath(path)
    path = os.path.expanduser(path)
    prev = os.getcwd()
    if path != prev:
        if mkdir:
            call('mkdir -p %(path)s' % locals(), verbose=verbose)
        os.chdir(path)
        curr = os.getcwd()
        sys.path.append(curr)
        if verbose:
            print('cd %s' % curr)
    try:
        yield
    finally:
        if path != prev:
            sys.path.remove(curr)
            os.chdir(prev)
            if verbose:
                print('cd %s' % prev)

def call(cmd, stdout=PIPE, stderr=PIPE, shell=True, nerf=False, throw=True, verbose=False):
    if verbose or nerf:
        print(cmd)
    if nerf:
        return (None, 'nerfed', 'nerfed')
    process = Popen(cmd, stdout=stdout, stderr=stderr, shell=shell)
    _stdout, _stderr = [stream.decode('utf-8') for stream in process.communicate()]
    exitcode = process.poll()
    if verbose:
        if _stdout:
            print(_stdout)
        if _stderr:
            print(_stderr)
    if throw and exitcode:
        raise CalledProcessError(exitcode, 'cmd=%(cmd)s; stdout=%(_stdout)s; stderr=%(_stderr)s' % locals())
    return exitcode, _stdout, _stderr

def rglob(pattern):
    matches = []
    # support for shell-like {x,y} syntax
    regex = re.compile('(.*){(.*)}(.*)')
    match = regex.search(pattern)
    if match:
        prefix, alternates, suffix = match.groups()
        for alternate in alternates.split(','):
            matches += rglob(prefix + alternate.strip() + suffix)
        return matches
    # support for recursive glob
    for r, _, fs in os.walk(os.path.dirname(pattern)):
        for f in fnmatch.filter(fs, os.path.basename(pattern)):
            matches.append(os.path.join(r, f))
    return matches

def globs(*paths):
    '''
    returns a set of all paths glob-matched
    '''
    return set([item for item in [glob.glob(path) for path in paths] for item in item])
