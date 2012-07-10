import os

from fabric.api import sudo
from fabric.decorators import task
from fabric.utils import puts

INSTALL_DIR = '/data'


@task
def create_project_structure(site_name):
    """Create directory structure for project `site_name`."""

    install_dir = os.path.join(INSTALL_DIR, site_name)
    dirs_to_create = (
        os.path.join(install_dir, 'releases'),
        os.path.join(install_dir, 'virtualenv'),
    )

    puts("Setup project structure at {0}".format(install_dir))
    sudo('mkdir -p {0}'.format(' '.join(dirs_to_create)))
