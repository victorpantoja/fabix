import os
from functools import partial

import cuisine
import fabric.api as fab

from fabix import get_config, get_project_name

_INSTALL_DIR = '/opt'
PYTHON_DOWNLOAD_URL = 'http://www.python.org/ftp/python/{version}/Python-{version}.tgz'
SETUPTOOLS_DOWNLOAD_URL = 'http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz'
SITES_DIR = '/data/sites/'


get_proj_config = get_config
get_config = partial(get_config, 'python')


@fab.task
def install(force=False):
    """Install python"""
    version = get_config()['version']

    install_dir = os.path.join(_INSTALL_DIR, 'python', version)
    python_bin = os.path.join(install_dir, 'bin', 'python')

    if cuisine.file_exists(python_bin):
        if not force:
            fab.puts("Python {0} found, skipping installation".format(version))
            return
        else:
            fab.puts("Reinstalling Python {0} found".format(version))

    fab.package_install(['build-essential', 'libcurl4-openssl-dev'])

    src_dir = fab.run('mktemp -d')
    with fab.cd(src_dir):
        fab.puts("Downloading python {0}".format(version))
        fab.run("wget -q '%s' -O - | tar xz" % PYTHON_DOWNLOAD_URL.format(version=version))
        with fab.cd('Python-{0}'.format(version)):
            fab.puts("Installing python {0}".format(version))
            fab.run("./configure --prefix=%s" % install_dir)
            fab.run("make")
            fab.sudo('make install')
    fab.run('rm -rf {0}'.format(src_dir))


def _python_bin_path(py_version, bin_name='python'):
    install_dir = os.path.join(_INSTALL_DIR, 'python', py_version)
    return os.path.join(install_dir, 'bin', bin_name)


@fab.task
def install_setuptools(force=False):
    """Install setuptools"""
    py_version = get_config()['version']

    easy_install_bin = _python_bin_path(py_version, 'easy_install')
    if cuisine.file_exists(easy_install_bin):
        if not force:
            fab.puts("easy_install for python {0} found, skipping installation".format(py_version))
            return
        else:
            fab.puts("Reinstalling easy_install for python {0}".format(py_version))

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
    version = get_config()['version']

    install_dir = os.path.join(_INSTALL_DIR, 'python')
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
    py_version = get_config()['version']

    fab.puts("Installing pypi package {0} on python {1}".format(package, py_version))

    if use_virtualenv:
        site = get_project_name()
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
        site = get_project_name()
        pip_bin = _get_virtualenv_bin(site, 'pip')
    else:
        pip_bin = _python_bin_path(py_version, 'pip')

    if not cuisine.file_exists(pip_bin):
        fab.puts("pip for version {0} not found".format(py_version))
        return

    fab.sudo('{cmd} uninstall --yes {package}'.format(cmd=pip_bin, package=package))


@fab.task
def create_virtualenv():
    """Create virtualenv for project."""
    site = get_project_name()
    version = get_config()['version']

    virtualenv_dir = "{}/{}/virtualenv".format(SITES_DIR, site)
    if cuisine.dir_exists(virtualenv_dir):
        fab.puts("virtualenv for {0} already exists".format(site))
        return

    with cuisine.mode_sudo():
        cuisine.dir_ensure(virtualenv_dir, recursive=True)

    venv_bin = _python_bin_path(version, 'virtualenv')
    fab.sudo("{venv_bin} {virtualenv_dir}".format(venv_bin=venv_bin,
             virtualenv_dir=virtualenv_dir))


def _get_virtualenv_bin(site, binary):
    """Grabs a binary in a given virtualenv"""
    bin_dir = os.path.join(SITES_DIR, site, 'virtualenv', 'bin')
    return os.path.join(bin_dir, binary)


@fab.task
def install_requirements(upgrade=False):
    """Install `site` project's requirements"""
    site = get_project_name()
    project_dir = get_proj_config()['project_dir']

    pip = _get_virtualenv_bin(site, 'pip')
    requirements = open("{}/requirements.txt".format(project_dir)).read().replace("\n", " ")
    fab.sudo("{pip} install {upgrade} {requirements}".format(
             pip=pip, upgrade="--upgrade" if upgrade else "",
             requirements=requirements))


@fab.task
def setup():
    """Install python, setuptools, pip and virtualenv."""
    install()
    install_setuptools()
    install_pip()
    install_pypi_package('virtualenv')
