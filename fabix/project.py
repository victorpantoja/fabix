import os
from datetime import datetime
from tempfile import mkdtemp

from cuisine import dir_ensure, mode_sudo
from fabric.context_managers import cd, lcd
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
def upload(site, tag='master'):
    """Upload project `site` files from tag or branch `master`."""
    puts("Upload project {0}".format(site))

    today = datetime.now().strftime('%Y%m%d-%H%M%S')
    commit_id = str(local('git rev-parse {0}'.format(tag), True)).strip()
    current = "%s-%s" % (today, commit_id[:8])

    with mode_sudo():
        dir_ensure(os.path.join(INSTALL_DIR, site, 'releases', current))

    local_temp_dir = mkdtemp()
    archive = os.path.join(local_temp_dir, '{0}.tar.gz'.format(site))

    git_arch_cmd = "git archive --format=tar.gz -o {archive} --prefix={commit_id}/ {commit_id}"
    local(git_arch_cmd.format(archive=archive, commit_id=commit_id))

    with lcd(local_temp_dir):
        remote_temp_dir = run('mktemp -d')
        put(archive, remote_temp_dir)
        with cd(remote_temp_dir):
            run("tar xzf {0}.tar.gz".format(site))
            sudo("mv {commit_id} {prefix}/{site}/releases/{current}".format(site=site, current=current, commit_id=commit_id, prefix=INSTALL_DIR))
        run('rm -rf {0}'.format(remote_temp_dir))
    local('rm -rf {0}'.format(local_temp_dir))

    return current


@task
def activate(project, release):
    """Activate release `release` code for project `project`."""
    puts("Activating project {0} release {1}".format(project, release))
    with cd(os.path.join(INSTALL_DIR, project)):
        sudo("ln -nsf releases/{release} {project}".format(project=project, release=release))


@task
def cleanup_old_releases(site, keep=5):
    """Cleanup old releases for `site` keeping the `keep` most recent."""

    with cd(os.path.join(INSTALL_DIR, site, 'releases')):
        files_to_remove = str(run('ls -1')).split()
        if files_to_remove:
            cmd_args = ' '.join(files_to_remove[:-keep])
            puts("Removing releases {0}".format(cmd_args))
            sudo('rm -rf {0}'.format(cmd_args))
