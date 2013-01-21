# coding: utf-8
import os
from StringIO import StringIO

import cuisine
from configobj import ConfigObj

import fabix


def install():
    """
    Install MongoDB server from 10gen repository.
    """
    fabix.system.apt_import_pubkey('7F0CEB10')
    fabix.system.apt_add_repository('10gen', 'dist', 'http://downloads-distro.mongodb.org/repo/ubuntu-upstart')
    cuisine.package_update()
    cuisine.package_install(['mongodb-10gen', 'ntp'])


def configure_instance(name, conf):
    """
    Add another mongodb instance configuration

    Normally you don't add an instance - this is only necessary when you want
    to run 2 mongod process on the same server.

    If you pass 'default' as the instance name, the default instance will be
    reconfigured.

    name: instance name, used in configuration and upstart scripts
    conf: configuration data for this instance
    """
    if name != 'default':
        config_file = '/etc/mongodb-{}.conf'.format(name)
    else:
        config_file = '/etc/mongodb.conf'.format(name)

    if cuisine.file_exists(config_file):
        content = cuisine.file_read(config_file)
    else:
        content = ''

    config = ConfigObj(infile=StringIO(content))
    for key, value in conf.items():
        config[key] = value

    config_buffer = StringIO()
    config.write(config_buffer)

    with cuisine.mode_sudo():
        cuisine.file_write(config_file, config_buffer.getvalue())
        if name != 'default':
            context = {
                'dbpath': config['dbpath'],
                'logpath': config['logpath'],
                'configfile': config_file,
            }
            init_file = os.path.join(os.path.dirname(__file__), 'support_files', 'etc', 'init', 'mongodb.conf')
            fabix.system.upstart.install(init_file, "mongodb-{}.conf".format(name), context)
