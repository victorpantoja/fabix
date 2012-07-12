import os

from fabric.context_managers import settings
from fabric.decorators import task
from fabric.operations import put, sudo
from fabric.utils import puts


@task
def restart_service(service, force_start=True, **kwargs):

    extra = ''
    for key, value in kwargs.iteritems():
        extra = "{0} {1}={2}".format(extra, key.upper(), value)

    if force_start:
        with settings(warn_only=True):
            status = sudo("service {0} status {1}".format(service, extra))
        if status.failed:
            cmd = 'start'
        else:
            cmd = 'restart'
    else:
        cmd = 'restart'
    sudo('service {0} {1} {2}'.format(service, cmd, extra))


@task
def reload_service(service):
    sudo('service {0} reload'.format(service))


@task
def upstart_install(file_name):
    init_name = os.path.basename(file_name)
    puts("Installing upstart config {0}".format(init_name))
    put(file_name, '/etc/init/{0}'.format(init_name), use_sudo=True)
