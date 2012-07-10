# coding: utf-8
import os

from cuisine import (dir_ensure, file_exists, file_local_read, file_upload,
    file_write, mode_sudo, package_ensure, text_template, user_ensure)
from fabric.api import cd, run, sudo
from fabric.contrib.console import confirm
from fabric.decorators import task
from fabric.utils import abort, puts

_INSTALL_DIR = '/opt'
_DOWNLOAD_URL = 'http://nginx.org/download/nginx-{version}.tar.gz'
NGINX_USER = 'nginx'
ETC_DIR = os.path.join(os.path.dirname(__file__), 'support_files', 'etc')


@task
def install_nginx(version, force=False):
    """Install nginx HTTP server."""

    package_ensure('libpcre3-dev')
    package_ensure('zlib1g-dev')
    package_ensure('build-essential')

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
            sudo('mkdir {0}'.format(os.path.join(install_dir, 'conf', 'sites-enabled')))
    run("rm -rf '{0}'".format(src_dir))


@task
def uninstall_nginx(version):
    """Uninstall nginx HTTP server"""

    install_dir = os.path.join(_INSTALL_DIR, 'nginx')
    if version != 'all':
        install_dir = os.path.join(install_dir, version)

    puts("Removing {0}".format(install_dir))
    if confirm("Are you sure?", default=False):
        sudo("rm -rf '{0}'".format(install_dir))
        puts("Nginx {0} uninstalled".format(version))


@task
def install_nginx_upstart(version):
    """Install nginx upstart config."""

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
def install_nginx_conf(version, nginx_file):
    """Install global nginx config."""

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
def install_nginx_site_conf(version, nginx_file):
    """Install nginx config per site."""

    if not os.path.exists(nginx_file):
        abort("Nginx conf {0} not found".format(nginx_file))

    site_name = os.path.basename(nginx_file)

    install_dir = os.path.join(_INSTALL_DIR, 'nginx', version)
    conf_file = os.path.join(install_dir, 'conf', 'sites-enabled', site_name)

    with mode_sudo():
        file_upload(conf_file, nginx_file)


@task
def setup_nginx(version, nginx_file, nginx_site_conf):
    """Installs and configures nginx"""
    install_nginx(version)
    install_nginx_upstart(version)
    install_nginx_conf(version, nginx_file)
    install_nginx_site_conf(version, nginx_site_conf)
