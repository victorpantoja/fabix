# coding: utf-8
import cuisine
import fabric.api as fab

import fabix


def install():
    fabix.system.apt_import_pubkey('7F0CEB10')
    fabix.system.apt_add_repository('10gen', 'dist', 'http://downloads-distro.mongodb.org/repo/ubuntu-upstart')
    cuisine.package_update()
    cuisine.package_upgrade()
    cuisine.package_install(['mongodb-10gen', 'ntp', 'lvm2'])


def change_datadir(datadir):
    with cuisine.mode_sudo():
        cuisine.dir_ensure(datadir, recursive=True)
    fab.sudo("chown -R mongodb:mongodb {}".format(datadir))
    fab.sudo("sed -i 's/^dbpath=\/var\/lib\/mongodb/dbpath={}/' /etc/mongodb.conf".format(datadir.replace('/', '\/')))
    fabix.system.upstart.restart('mongodb', force_start=True)
