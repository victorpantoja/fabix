import os
#from functools import partial

import cuisine
import fabric.api as fab

from fabix.project import current_project

#from fabix import get_config, get_project_name

PYTHON_DOWNLOAD_URL = 'http://www.python.org/ftp/python/{version}/Python-{version}.tgz'
SETUPTOOLS_DOWNLOAD_URL = 'http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz'
#SITES_DIR = '/data/sites/'

#get_proj_config = get_config
#get_config = partial(get_config, 'python')


DEFAULT_CONFIG = {
    'version': '2.7.3',
    'install_dir': '/opt',
}


def get_config():
    custom_config = fab.env.fabix.get('python', {})
    config = dict(DEFAULT_CONFIG)
    config.update(custom_config)
    return config


def setup():
    """Install python, setuptools, pip and virtualenv."""
    install()
    install_setuptools()
    install_pip()
    #install_pypi_package('virtualenv', False)


def install(force_install=False):
    """Install python"""

    config = get_config()

    version = config['version']
    install_dir = os.path.join(config['install_dir'], 'python', version)

    if is_installed(version):
        if not force_install:
            fab.puts("Python {} found, skipping installation".format(version))
            return
        else:
            fab.puts("Reinstalling python {}".format(version))

    cuisine.package_install(['build-essential', 'libcurl4-openssl-dev'])

    src_dir = fab.run('mktemp -d')
    with fab.cd(src_dir):
        fab.puts("Downloading python {}".format(version))
        url = PYTHON_DOWNLOAD_URL.format(version=version)
        fab.run("wget -q '{}' -O - | tar xz".format(url))
        with fab.cd('Python-{}'.format(version)):
            fab.puts("Installing python {}".format(version))
            fab.run("./configure --prefix={}".format(install_dir))
            fab.run("make")
            fab.sudo('make install')
    fab.run('rm -rf {}'.format(src_dir))


def is_installed(version):
    """Check if specified python version is installed"""
    config = get_config()
    if not version:
        version = config['version']

    python_bin = os.path.join(config['install_dir'], 'python', version, 'bin',
                              'python{}'.format(version[0:3]))

    return cuisine.file_exists(python_bin)


def has_setuptools():
    config = get_config()
    version = config['version']

    bin_file = os.path.join(version, 'easy_install')
    return cuisine.file_exists(bin_file)


def _python_bin_path(py_version, bin_name='python'):
    install_dir = os.path.join(DEFAULT_CONFIG['install_dir'], 'python', py_version)
    return os.path.join(install_dir, 'bin', bin_name)


def install_setuptools(force=False):
    """Install setuptools"""
    config = get_config()
    py_version = config['version']

    if not is_installed(py_version):
        fab.abort("Can't install setuptools without python {}".format(py_version))
        return

    easy_install_bin = _python_bin_path(py_version, 'easy_install')
    if cuisine.file_exists(easy_install_bin):
        if not force:
            fab.puts("easy_install for python {} found, skipping installation".format(py_version))
            return
        else:
            fab.puts("Reinstalling easy_install for python {}".format(py_version))

    major, minor = py_version.split('.')[0:2]
    version = "{0}.{1}".format(major, minor)

    python_bin = _python_bin_path(py_version)

    src_dir = fab.run('mktemp -d')
    with fab.cd(src_dir):
        fab.puts("Downloading setuptools for python {0}".format(version))
        download_url = SETUPTOOLS_DOWNLOAD_URL.format(py_version=version)
        fab.run("wget -q '{0}' -O - | tar xz".format(download_url))
        with fab.cd('setuptools-*'):
            fab.puts("Installing setuptools for python {0}".format(version))
            fab.sudo("{0} setup.py install".format(python_bin))
    fab.sudo('rm -rf {0}'.format(src_dir))


@fab.task
def uninstall_setuptools():
    """Uninstall setuptools"""
    py_version = get_config()['version']

    major, minor = py_version.split('.')[0:2]
    version = "{0}.{1}".format(major, minor)

    python_bin = _python_bin_path(py_version)

    src_dir = fab.run('mktemp -d')
    with fab.cd(src_dir):
        fab.puts("Downloading setuptools for python {0}".format(version))
        download_url = SETUPTOOLS_DOWNLOAD_URL.format(py_version=version)
        fab.run("wget -q '{0}' -O - | tar xz".format(download_url))
        with fab.cd('setuptools-*'):
            fab.puts("Uninstalling setuptools for python {0}".format(version))
            fab.sudo("{0} setup.py install --record setuptools_files.txt".format(python_bin))
            fab.sudo("cat setuptools_files.txt | xargs rm -rf")
    fab.sudo('rm -rf {0}'.format(src_dir))


@fab.task
def uninstall():
    """Uninstall python"""
    config = get_config()
    version = config['version']

    install_dir = os.path.join(config['install_dir'], 'python')
    if version != 'all':
        install_dir = os.path.join(install_dir, version)

    fab.puts("Removing {0}".format(install_dir))
    if fab.confirm("Are you sure?", default=False):
        fab.sudo("rm -rf '{0}'".format(install_dir))
        fab.puts("Python {0} uninstalled".format(version))


@fab.task
def install_pip():
    """Install pip latest version."""
    py_version = get_config()['version']

    fab.puts("Installing pip for python {0}".format(py_version))
    easy_install_bin = _python_bin_path(py_version, 'easy_install')

    if not cuisine.file_exists(easy_install_bin):
        fab.puts("easy_install for version {0} not found".format(py_version))
        return

    fab.sudo('{0} pip'.format(easy_install_bin))


@fab.task
def install_pypi_package(package, use_virtualenv=True):
    """Install pypi package `package` on python `py_version`."""
    config = get_config()
    py_version = config['version']

    fab.puts("Installing pypi package {0} on python {1}".format(package, py_version))

    if use_virtualenv:
        site = current_project()
        pip_bin = _get_virtualenv_bin(site, 'pip')
    else:
        pip_bin = _python_bin_path(py_version, 'pip')

    if not cuisine.file_exists(pip_bin):
        fab.puts("pip for version {0} not found".format(py_version))
        return

    fab.sudo('{cmd} install {package}'.format(cmd=pip_bin, package=package))


@fab.task
def uninstall_pypi_package(package, use_virtualenv=True):
    """Uninstall pypi package `package` on python `py_version`."""
    py_version = get_config()['version']

    fab.puts("Uninstalling pypi package {0} on python {1}".format(package, py_version))

    if use_virtualenv:
        site = current_project()
        pip_bin = _get_virtualenv_bin(site, 'pip')
    else:
        pip_bin = _python_bin_path(py_version, 'pip')

    if not cuisine.file_exists(pip_bin):
        fab.puts("pip for version {0} not found".format(py_version))
        return

    fab.sudo('{cmd} uninstall --yes {package}'.format(cmd=pip_bin, package=package))


def create_virtualenv():
    """Create virtualenv for project."""
    site = current_project()
    config = get_config()
    version = config['version']

    install_project_dir = fab.env.fabix[site]['install_project_dir']
    project_dir = '{0}/sites/{1}/'.format(install_project_dir, site)

    virtualenv_dir = "{}/virtualenv".format(project_dir)
    if cuisine.dir_exists(virtualenv_dir + "/bin"):
        fab.puts("virtualenv for {0} already exists".format(site))
        return

    with cuisine.mode_sudo():
        cuisine.dir_ensure(virtualenv_dir, recursive=True)

    venv_bin = _python_bin_path(version, 'virtualenv')
    fab.sudo("{venv_bin} {virtualenv_dir}".format(venv_bin=venv_bin,
             virtualenv_dir=virtualenv_dir))


def _get_virtualenv_bin(site, binary):
    """Grabs a binary in a given virtualenv"""
    site = current_project()

    install_project_dir = fab.env.fabix[site]['install_project_dir']
    project_dir = '{0}/sites/{1}/'.format(install_project_dir, site)

    bin_dir = os.path.join(project_dir, 'virtualenv', 'bin')
    return os.path.join(bin_dir, binary)


def install_requirements(release, upgrade=False):
    """Install `site` project's requirements"""
    site = current_project()

    install_project_dir = fab.env.fabix[site]['install_project_dir']
    project_dir = '{0}/sites/{1}/releases/{2}'.format(install_project_dir, site, release)

    pip = _get_virtualenv_bin(site, 'pip')
    #requirements = open("{}/requirements.txt".format(project_dir)).read().replace("\n", " ")
    fab.sudo("{pip} install {upgrade} -r {project}/requirements.txt".format(
             pip=pip, upgrade="--upgrade" if upgrade else "",
             project=project_dir))
