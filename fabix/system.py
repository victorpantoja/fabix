import os

from cuisine import upstart_ensure
from fabric.decorators import task
from fabric.operations import put, sudo
from fabric.utils import puts


@task
def restart_service(service, force_start=True):
    if force_start:
        upstart_ensure(service)
    else:
        sudo('service {0} restart'.format(service))


@task
def reload_service(service):
    sudo('service {0} reload'.format(service))


@task
def upstart_install(file_name):
    init_name = os.path.basename(file_name)
    puts("Installing upstart config {0}".format(init_name))
    put(file_name, '/etc/init/{0}'.format(init_name), use_sudo=True)
