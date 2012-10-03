# coding: utf-8
import os
from functools import partial

from cuisine import (dir_ensure, file_exists, file_local_read, file_upload,
    file_write, mode_sudo, text_template, user_ensure, package_install)
from fabric.api import cd, run, sudo, env
from fabric.contrib.console import confirm
from fabric.decorators import task
from fabric.utils import abort, puts

from fabix import get_config

_INSTALL_DIR = '/opt'
_DOWNLOAD_URL = 'http://nginx.org/download/nginx-{version}.tar.gz'
NGINX_USER = 'nginx'
ETC_DIR = os.path.join(os.path.dirname(__file__), 'support_files', 'etc')


get_config = partial(get_config, 'nginx')


@task
def install(force=False):
    """Install nginx HTTP server."""
    version = get_config()['version']

    package_install(['build-essential', 'libpcre3-dev', 'zlib1g-dev'])

    install_dir = os.path.join(_INSTALL_DIR, 'nginx', version)
    nginx_bin = os.path.join(install_dir, 'sbin', 'nginx')
    if file_exists(nginx_bin):
        if not force:
            puts("Nginx {0} found, skipping installation".format(version))
            return
        else:
            puts("Reinstalling nginx {0} found".format(version))

    with mode_sudo():
        dir_ensure(install_dir, True)

    home_dir = os.path.join(install_dir, 'html')
    user_ensure(NGINX_USER, None, home_dir, shell='/sbin/nologin')
    sudo('passwd -l nginx')

    download_url = _DOWNLOAD_URL.format(version=version)

    src_dir = run('mktemp -d')
    with cd(src_dir):
        puts("Downloading nginx {0}".format(version))
        run("wget -q '{0}' -O - | tar xz".format(download_url))
        with cd('nginx-{0}'.format(version)):
            puts("Compiling nginx {0}".format(version))
            run("./configure --prefix={0} --with-http_stub_status_module".format(install_dir))
            run("make")
            puts("Installing nginx {0}".format(version))
            sudo('make install')
            with mode_sudo():
                dir_ensure("{0}{1}".format(install_dir, '/conf/sites-enabled'))
    run("rm -rf '{0}'".format(src_dir))


@task
def uninstall():
    """Uninstall nginx HTTP server"""
    version = get_config()['version']

    install_dir = os.path.join(_INSTALL_DIR, 'nginx')
    if version != 'all':
        install_dir = os.path.join(install_dir, version)

    puts("Removing {0}".format(install_dir))
    if confirm("Are you sure?", default=False):
        sudo("rm -rf '{0}'".format(install_dir))
        puts("Nginx {0} uninstalled".format(version))


@task
def install_upstart():
    """Install nginx upstart config."""
    version = get_config()['version']

    install_dir = os.path.join(_INSTALL_DIR, 'nginx', version)
    nginx_bin = os.path.join(install_dir, 'sbin', 'nginx')
    nginx_pid = os.path.join(install_dir, 'logs', 'nginx.pid')

    context = {
        'nginx_bin': nginx_bin,
        'nginx_pid': nginx_pid,
    }

    nginx_tpl = os.path.join(ETC_DIR, 'init', 'nginx.conf')
    tpl_content = file_local_read(nginx_tpl)
    content = text_template(tpl_content, context)

    with mode_sudo():
        file_write('/etc/init/nginx.conf', content)


@task
def put_conf(nginx_file):
    """Install global nginx config."""
    version = get_config()['version']

    install_dir = os.path.join(_INSTALL_DIR, 'nginx', version)
    conf_file = os.path.join(install_dir, 'conf', 'nginx.conf')

    if not os.path.exists(nginx_file):
        abort("Nginx conf {0} not found".format(nginx_file))

    nginx_pid = os.path.join(install_dir, 'logs', 'nginx.pid')

    context = {
        'nginx_user': NGINX_USER,
        'nginx_pid': nginx_pid,
    }

    tpl_content = open(nginx_file, 'rb').read()
    content = text_template(tpl_content, context)

    with mode_sudo():
        file_write(conf_file, content)


@task
def put_site_conf(nginx_file, context=None):
    """Install nginx config per site."""
    version = get_config()['version']

    if not os.path.exists(nginx_file):
        abort("Nginx conf {0} not found".format(nginx_file))

    site_name = os.path.basename(nginx_file)

    install_dir = os.path.join(_INSTALL_DIR, 'nginx', version)
    conf_file = os.path.join(install_dir, 'conf', 'sites-enabled', site_name)

    if context:
        tpl_content = open(nginx_file, 'rb').read()
        content = text_template(tpl_content, context)

        with mode_sudo():
            file_write(conf_file, content)
    else:
        with mode_sudo():
            file_upload(conf_file, nginx_file)


@task
def setup(nginx_file, nginx_site_conf):
    """Installs and configures nginx"""
    install()
    install_upstart()
    put_conf(nginx_file)
    put_site_conf(nginx_site_conf)
