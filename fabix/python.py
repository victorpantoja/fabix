import os

from cuisine import (file_exists, package_ensure)
from fabric.api import cd, run, sudo
from fabric.contrib.console import confirm
from fabric.decorators import task
from fabric.utils import puts

_INSTALL_DIR = '/opt'
PYTHON_DOWNLOAD_URL = 'http://www.python.org/ftp/python/{version}/Python-{version}.tgz'
SETUPTOOLS_DOWNLOAD_URL = 'http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz'
SITES_DIR = '/data/sites/'


@task
def install_python(version, force=False):
    """Install python"""

    package_ensure('build-essential')
    package_ensure('libcurl4-openssl-dev')

    install_dir = os.path.join(_INSTALL_DIR, 'python', version)
    python_bin = os.path.join(install_dir, 'bin', 'python')

    if file_exists(python_bin):
        if not force:
            puts("Python {0} found, skipping installation".format(version))
            return
        else:
            puts("Reinstalling Python {0} found".format(version))

    src_dir = run('mktemp -d')
    with cd(src_dir):
        puts("Downloading python {0}".format(version))
        run("wget -q '%s' -O - | tar xz" % PYTHON_DOWNLOAD_URL.format(version=version))
        with cd('Python-{0}'.format(version)):
            puts("Installing python {0}".format(version))
            run("./configure --prefix=%s" % install_dir)
            run("make")
            sudo('make install')
    run('rm -rf {0}'.format(src_dir))


def _python_bin_path(py_version, bin_name='python'):
    install_dir = os.path.join(_INSTALL_DIR, 'python', py_version)
    return os.path.join(install_dir, 'bin', bin_name)


@task
def install_setuptools(py_version):
    """Install setuptools"""

    major, minor = py_version.split('.')[0:2]
    version = "{0}.{1}".format(major, minor)

    python_bin = _python_bin_path(py_version)

    src_dir = run('mktemp -d')
    with cd(src_dir):
        puts("Downloading setuptools for python {0}".format(version))
        download_url = SETUPTOOLS_DOWNLOAD_URL.format(py_version=version)
        run("wget -q '{0}' -O - | tar xz".format(download_url))
        with cd('setuptools-*'):
            puts("Installing setuptools for python {0}".format(version))
            sudo("{0} setup.py install".format(python_bin))
    sudo('rm -rf {0}'.format(src_dir))


@task
def uninstall_setuptools(py_version):
    """Uninstall setuptools"""

    major, minor = py_version.split('.')[0:2]
    version = "{0}.{1}".format(major, minor)

    python_bin = _python_bin_path(py_version)

    src_dir = run('mktemp -d')
    with cd(src_dir):
        puts("Downloading setuptools for python {0}".format(version))
        download_url = SETUPTOOLS_DOWNLOAD_URL.format(py_version=version)
        run("wget -q '{0}' -O - | tar xz".format(download_url))
        with cd('setuptools-*'):
            puts("Uninstalling setuptools for python {0}".format(version))
            sudo("{0} setup.py install --record setuptools_files.txt".format(python_bin))
            sudo("cat setuptools_files.txt | xargs rm -rf")
    sudo('rm -rf {0}'.format(src_dir))


@task
def uninstall_python(version):
    """Uninstall python"""

    install_dir = os.path.join(_INSTALL_DIR, 'python')
    if version != 'all':
        install_dir = os.path.join(install_dir, version)

    puts("Removing {0}".format(install_dir))
    if confirm("Are you sure?", default=False):
        sudo("rm -rf '{0}'".format(install_dir))
        puts("Python {0} uninstalled".format(version))


@task
def install_pip(py_version):
    """Install pip latest version."""

    puts("Installing pip for python {0}".format(py_version))
    easy_install_bin = _python_bin_path(py_version, 'easy_install')

    if not file_exists(easy_install_bin):
        puts("easy_install for version {0} not found".format(py_version))
        return

    sudo('{0} pip'.format(easy_install_bin))


@task
def uninstall_pip(py_version):
    """Uninstall pip

    This task is just a alias to uninstall_pypi_package.
    """
    uninstall_pypi_package(py_version, 'pip')


@task
def install_pypi_package(py_version, package):
    """Install pypi package `package` on python `py_version`."""

    puts("Installing pypi package {0} on python {1}".format(package, py_version))
    pip_bin = _python_bin_path(py_version, 'pip')

    if not file_exists(pip_bin):
        puts("pip for version {0} not found".format(py_version))
        return

    sudo('{cmd} install {package}'.format(cmd=pip_bin, package=package))


@task
def uninstall_pypi_package(py_version, package):
    """Uninstall pypi package `package` on python `py_version`."""

    puts("Uninstalling pypi package {0} on python {1}".format(package, py_version))
    pip_bin = _python_bin_path(py_version, 'pip')

    if not file_exists(pip_bin):
        puts("pip for version {0} not found".format(py_version))
        return

    sudo('{cmd} uninstall {package}'.format(cmd=pip_bin, package=package))


@task
def create_virtualenv(version, site):
    """Cria a virtualenv para um site, :site"""
    venv_bin = _python_bin_path(version, 'virtualenv')
    sudo("{venv_bin} {sites_dir}/{site}/virtualenv".format(venv_bin=venv_bin,
        sites_dir=SITES_DIR,
        site=site))


def _get_virtualenv_bin(site, binary):
    """Grabs a binary in a given virtualenv"""
    bin_dir = os.path.join(SITES_DIR, site, 'virtualenv', 'bin')
    return os.path.join(bin_dir, binary)


@task
def install_requirements(site, upgrade=False):
    """Install `site` project's requirements"""
    pip = _get_virtualenv_bin(site, 'pip')
    requirements = open("requirements.txt").read().replace("\n", " ")
    sudo("{pip} install {upgrade} {requirements}".format(
            pip=pip,
            upgrade="--upgrade" if upgrade else "",
            requirements=requirements))


@task
def setup_python(version):
    """Install python, setuptools, pip and virtualenv."""
    install_python(version)
    install_setuptools(version)
    install_pip(version)
    install_pypi_package(version, 'virtualenv')
