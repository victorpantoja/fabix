# coding: utf-8
import time

import fabric.api as fab

from fabix.system import upstart


@fab.task
def ssh():
    fab.puts("Opening shell to host {0}".format(fab.env.host_string))
    fab.open_shell()


@fab.task
def apt_import_pubkey(key, keyserver='keyserver.ubuntu.com'):
    fab.puts("Importing pubkey {0}".format(key))
    fab.sudo('apt-key adv --keyserver {0} --recv {1}'.format(keyserver, key))


@fab.task
def apt_add_repository(name, distro, url):
    fab.puts("Add repository {0}".format(name))
    fab.sudo("echo 'deb {0} {1} {2}' | sudo tee /etc/apt/sources.list.d/{2}.list".format(url, distro, name))


@fab.task
def reboot():
    fab.puts("Rebooting machine in 5 seconds!")
    # just some time so user can press Ctrl+C
    time.sleep(5)
    fab.sudo('reboot')
