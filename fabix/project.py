import os
from datetime import datetime

from fabric.api import cd
from fabric.decorators import task
from fabric.operations import local, put, run, sudo
from fabric.utils import puts

INSTALL_DIR = '/data/sites'


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


@task
def upload(site):
    """Upload project `site` files."""

    puts("Upload project %s" % site)

    # Generate package file
    today = datetime.now().strftime('%Y%m%d-%H%M%S')
    commit_id = str(local('git rev-parse HEAD', True)).strip()
    current = "%s-%s" % (today, commit_id[:8])

    local("rm -f /tmp/{0}.tgz".format(site))
    git_arch_cmd = r"""git archive --format=tar --prefix={commit_id}/ {commit_id} | gzip > /tmp/{site}.tgz"""
    local(git_arch_cmd.format(site=site, commit_id=commit_id))

    put("/tmp/{0}.tgz".format(site), "/tmp/")
    run("tar -C /tmp -zxf /tmp/{0}.tgz".format(site))
    sudo("mv /tmp/{commit_id} {prefix}/{site}/releases/{current}".format(site=site, current=current, commit_id=commit_id, prefix=INSTALL_DIR))

    puts("Activating site %s" % site)
    with cd(os.path.join(INSTALL_DIR, site)):
        sudo("ln -nsf releases/{current} {site}".format(site=site, current=current))

    #_cleanup_old_releases(site)

