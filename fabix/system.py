from cuisine import upstart_ensure
from fabric.api import sudo
from fabric.decorators import task


@task
def restart_service(service, force_start=True):
    if force_start:
        upstart_ensure(service)
    else:
        sudo('service {0} restart').format(service))

@task
def reload_service(service):
    sudo('service {0} reload'.format(service))
