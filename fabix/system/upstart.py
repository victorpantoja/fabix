# coding: utf-8
import os

import fabric.api as fab


def install(filename):
    """Install upstart script on remote host.

    filename will be uploaded to /etc/init on remote server."""
    name = os.path.basename(filename)
    fab.put(filename, '/etc/init/{0}'.format(name), use_sudo=True)


@fab.task
def start(name, **kwargs):
    """Start specified upstart job.

    If **kwargs is specified, then they will be passed on command line
    as variables to upstart script.

    For example, to start a service called foo:
        `fab start:foo`
    If you want to pass a variable PORT to upstart script:
        `fab start:foo,PORT=12345`
    """
    args = ' '.join(['{}={}'.format(k, v) for k, v in kwargs.iteritems()])
    fab.sudo("start {name} {args}".format(name=name, args=args))


@fab.task
def stop(name, **kwargs):
    """Stop specified upstart job.

    If **kwargs is specified, then they will be passed on command line
    as variables to upstart script.

    For example, to stop a service called foo:
        `fab stop:foo`
    If you want to pass a variable PORT to upstart script:
        `fab stop:foo,PORT=12345`

    If you pass any variable to upstart on initialization, the same variables
    must be passed to stop.
    """
    args = ' '.join(['{}={}'.format(k, v) for k, v in kwargs.iteritems()])
    fab.sudo("stop {name} {args}".format(name=name, args=args))


@fab.task
def reload(name, **kwargs):
    """Reload specified upstart job.

    If **kwargs is specified, then they will be passed on command line
    as variables to upstart script.

    For example, to reload a service called foo:
        `fab reload:foo`
    If you want to pass a variable PORT to upstart script:
        `fab reload:foo,PORT=12345`

    If you pass any variable to upstart on initialization, the same variables
    must be passed to reload.
    """
    args = ' '.join(['{}={}'.format(k, v) for k, v in kwargs.iteritems()])
    fab.sudo("reload {name} {args}".format(name=name, args=args))


@fab.task
def restart(name, force_start=True, **kwargs):
    """Restart specified upstart job.

    If force_start is true, then the job will be started if it isn't running.

    If **kwargs is specified, then they will be passed on command line
    as variables to upstart script.

    For example, to restart a service called foo:
        `fab restart:foo`
    If you want to pass a variable PORT to upstart script:
        `fab reload:foo,PORT=12345`

    If you pass any variable to upstart on initialization, the same variables
    must be passed to restart.
    """
    args = ' '.join(['{}={}'.format(k, v) for k, v in kwargs.iteritems()])

    cmd = 'restart'
    if force_start:
        with fab.settings(warn_only=True):
            status = fab.sudo("status {name} {args}".format(name=name, args=args))
        if status.failed:
            cmd = 'start'
    fab.sudo("{cmd} {name} {args}".format(cmd=cmd, name=name, args=args))


@fab.task
def disable(name):
    """
    Disable specified upstart job
    """
    fab.sudo("echo 'manual' | tee /etc/init/{}.override".format(name))
