#!/usr/bin/env python

import os
import re
import sys
from pprint import pprint
from contextlib import contextmanager
from subprocess import Popen, PIPE

sys.dont_write_bytecode = True

class NoDefaultOrDecomposedValueForGiturl(Exception):
    pass

@contextmanager
def cd(*args, **kwargs):
    mkdir = kwargs.pop('mkdir', True)
    path = os.path.sep.join(args)
    path = os.path.normpath(path)
    path = os.path.expanduser(path)
    prev = os.getcwd()
    if path != prev:
        if mkdir:
            run('mkdir -p %(path)s' % locals())
        os.chdir(path)
        curr = os.getcwd()
        sys.path.append(curr)
    try:
        yield
    finally:
        if path != prev:
            sys.path.remove(curr)
            os.chdir(prev)

def run(*args, **kwargs):
    process = Popen(
        shell=kwargs.pop('shell', True),
        stdout=kwargs.pop('stdout', PIPE),
        stderr=kwargs.pop('stderr', PIPE),
        *args, **kwargs)
    stdout, stderr = process.communicate()
    exitcode = process.poll()
    return exitcode, stdout.strip(), stderr.strip()

def expand(path):
    if path:
        return os.path.expanduser(path)

def decompose(repospec, giturl=None):
    regex = re.compile('((git|ssh|https?|rsync)://)(\w+@)?([\w\.]+)(:(\d+))?[:/]{1,2}')
    match = regex.match(repospec)
    if match:
        giturl = match.group()
        reponame = os.path.splitext(repospec[len(giturl):])[0]
    else:
        reponame = repospec
    if giturl:
        return giturl, reponame, 'master'
    raise NoDefaultOrDecomposedValueForGiturl

def lsremote(repourl):
    return run('git ls-remote ' + repourl)

def divine(giturl, reponame, revision):
    r2c = {}
    c2r = {}
    result = lsremote(giturl + reponame)[1]
    for line in result.split('\n'):
        commit, refname = line.split('\t')
        r2c[refname] = commit
        c2r[commit] = refname

    refnames = [
        'refs/heads/' + revision,
        'refs/tags/' + revision,
        revision
    ]

    commit = None
    for refname in refnames:
        commit = r2c.get(refname, None)
        if commit:
            break

    if not commit:
        commit = revision

    return c2r.get(commit, None), commit

def clone(giturl, reponame, commit, clonepath, mirrorpath, versioning=False):
    clonepath = expand(clonepath)
    mirrorpath = expand(mirrorpath)
    mirror = ''
    if mirrorpath:
        mirror = '--reference %(mirrorpath)s/%(reponame)s.git' % locals()
    path = os.path.join(clonepath, reponame)
    repopath = reponame
    if versioning:
        repopath = os.path.join(repopath, commit)
    with cd(clonepath, mkdir=True):
        if not os.path.isdir(repopath):
            run('git clone %(mirror)s %(giturl)s%(reponame)s %(repopath)s' % locals())
        with cd(repopath):
            run('git clean -xfd')
            run('git checkout %(commit)s' % locals())
    return os.path.join(clonepath, repopath)
