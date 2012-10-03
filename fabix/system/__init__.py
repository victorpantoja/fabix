import os
import time

from fabric.api import env
from fabric.context_managers import settings
from fabric.decorators import task
from fabric.operations import open_shell, put, sudo
from fabric.utils import puts


@task
def ssh():
    puts("Opening shell to host {0}".format(env.host_string))
    open_shell()


@task
def apt_import_pubkey(key, keyserver='keyserver.ubuntu.com'):
    puts("Importing pubkey {0}".format(key))
    sudo('apt-key adv --keyserver {0} --recv {1}'.format(keyserver, key))


@task
def apt_add_repository(name, distro, url):
    puts("Add repository {0}".format(name))
    sudo("echo 'deb {0} {1} {2}' | sudo tee /etc/apt/sources.list.d/{2}.list".format(url, distro, name))


@task
def reboot():
    puts("Rebooting machine in 5 seconds!")
    # just some time so user can press Ctrl+C
    time.sleep(5)
    sudo('reboot')
