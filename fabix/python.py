import os

from cuisine import (file_exists, package_ensure)
from fabric.api import cd, run, sudo
from fabric.decorators import task
from fabric.utils import puts

_INSTALL_DIR = '/opt'
PYTHON_DOWNLOAD_URL = 'http://www.python.org/ftp/python/{version}/Python-{version}.tgz'
SETUPTOOLS_DOWNLOAD_URL = 'http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz'


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


@task
def install_setuptools(py_version):
    """Install setuptools"""

    major, minor = py_version.split('.')[0:2]
    version = "{0}.{1}".format(major, minor)

    python_install_dir = os.path.join(_INSTALL_DIR, 'python', py_version)
    python_bin = os.path.join(python_install_dir, 'bin', 'python')

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

    python_install_dir = os.path.join(_INSTALL_DIR, 'python', py_version)
    python_bin = os.path.join(python_install_dir, 'bin', 'python')

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
