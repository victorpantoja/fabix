# coding: utf-8
import os

import cuisine
import fabric.api as fab


_DOWNLOAD_URL = 'http://nginx.org/download/nginx-{version}.tar.gz'
ETC_DIR = os.path.join(os.path.dirname(__file__), 'support_files', 'etc')


DEFAULT_CONFIG = {
    'version': '1.3.7',
    'install_dir': '/opt',
    'user': 'nginx',
}


def get_config():
    custom_config = fab.env.fabix.get('python', {})
    config = dict(DEFAULT_CONFIG)
    config.update(custom_config)
    return config


def install(force=False):
    """Install nginx HTTP server."""
    config = get_config()
    version = config['version']

    cuisine.package_install(['build-essential', 'libpcre3-dev', 'zlib1g-dev'])

    install_dir = os.path.join(config['install_dir'], 'nginx', version)
    nginx_bin = os.path.join(install_dir, 'sbin', 'nginx')
    if cuisine.file_exists(nginx_bin):
        if not force:
            fab.puts("Nginx {0} found, skipping installation".format(version))
            return
        else:
            fab.puts("Reinstalling nginx {0} found".format(version))

    with cuisine.mode_sudo():
        cuisine.dir_ensure(install_dir, True)

    home_dir = os.path.join(install_dir, 'html')
    cuisine.user_ensure(config['user'], None, home_dir, shell='/sbin/nologin')
    fab.sudo('passwd -l nginx')

    download_url = _DOWNLOAD_URL.format(version=version)

    src_dir = fab.run('mktemp -d')
    with fab.cd(src_dir):
        fab.puts("Downloading nginx {0}".format(version))
        fab.run("wget -q '{0}' -O - | tar xz".format(download_url))
        with fab.cd('nginx-{0}'.format(version)):
            fab.puts("Compiling nginx {0}".format(version))
            fab.run("./configure --prefix={0} --with-http_stub_status_module".format(install_dir))
            fab.run("make")
            fab.puts("Installing nginx {0}".format(version))
            fab.sudo('make install')
            with cuisine.mode_sudo():
                cuisine.dir_ensure("{0}{1}".format(install_dir, '/conf/sites-enabled'))
    fab.run("rm -rf '{0}'".format(src_dir))


@fab.task
def uninstall():
    """Uninstall nginx HTTP server"""
    config = get_config()
    version = config['version']

    install_dir = os.path.join(config['install_dir'], 'nginx')
    if version != 'all':
        install_dir = os.path.join(install_dir, version)

    fab.puts("Removing {0}".format(install_dir))
    if fab.confirm("Are you sure?", default=False):
        fab.sudo("rm -rf '{0}'".format(install_dir))
        fab.puts("Nginx {0} uninstalled".format(version))


@fab.task
def install_upstart():
    """Install nginx upstart config."""
    config = get_config()
    version = config['version']

    install_dir = os.path.join(config['install_dir'], 'nginx', version)
    nginx_bin = os.path.join(install_dir, 'sbin', 'nginx')
    nginx_pid = os.path.join(install_dir, 'logs', 'nginx.pid')

    context = {
        'nginx_bin': nginx_bin,
        'nginx_pid': nginx_pid,
    }

    nginx_tpl = os.path.join(ETC_DIR, 'init', 'nginx.conf')
    tpl_content = cuisine.file_local_read(nginx_tpl)
    content = cuisine.text_template(tpl_content, context)

    with cuisine.mode_sudo():
        cuisine.file_write('/etc/init/nginx.conf', content)


@fab.task
def put_conf(nginx_file):
    """Install global nginx config."""
    config = get_config()
    version = config['version']

    install_dir = os.path.join(config['install_dir'], 'nginx', version)
    conf_file = os.path.join(install_dir, 'conf', 'nginx.conf')

    if not os.path.exists(nginx_file):
        fab.abort("Nginx conf {0} not found".format(nginx_file))

    nginx_pid = os.path.join(install_dir, 'logs', 'nginx.pid')

    context = {
        'nginx_user': config['user'],
        'nginx_pid': nginx_pid,
    }

    tpl_content = open(nginx_file, 'rb').read()
    content = cuisine.text_template(tpl_content, context)

    with cuisine.mode_sudo():
        cuisine.file_write(conf_file, content)


@fab.task
def put_site_conf(nginx_file, context=None):
    """Install nginx config per site."""
    config = get_config()
    version = config['version']

    if not os.path.exists(nginx_file):
        fab.abort("Nginx conf {0} not found".format(nginx_file))

    site_name = os.path.basename(nginx_file)

    install_dir = os.path.join(config['install_dir'], 'nginx', version)
    conf_file = os.path.join(install_dir, 'conf', 'sites-enabled', site_name)

    if context:
        tpl_content = open(nginx_file, 'rb').read()
        content = cuisine.text_template(tpl_content, context)

        with cuisine.mode_sudo():
            cuisine.file_write(conf_file, content)
    else:
        with cuisine.mode_sudo():
            cuisine.file_upload(conf_file, nginx_file)


@fab.task
def setup(nginx_file, nginx_site_conf):
    """Installs and configures nginx"""
    install()
    install_upstart()
    put_conf(nginx_file)
    put_site_conf(nginx_site_conf)
