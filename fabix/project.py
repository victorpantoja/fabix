import os
from datetime import datetime
from tempfile import mkdtemp

import cuisine
import fabric.api as fab

from fabix import get_config

INSTALL_DIR = '/data/sites'


class env(object):
    def __init__(self, project_name):
        self._old_env_name = None
        self._current_env_name = project_name
        if 'fabix' in fab.env:
            self._old_env_name = fab.env.get('fabix', dict()).get('_current_project', None)

    def __enter__(self):
        fab.env.fabix['_current_project'] = self._current_env_name

    def __exit__(self, type, value, traceback):
        if self._old_env_name is not None:
            fab.env.fabix['_current_project'] = self._old_env_name


@fab.task
def upload(tag='master'):
    """Upload project `site` files from tag or branch `master`."""
    site = fab.env.fabix['_current_project']
    project_dir = get_config()['project_dir']

    install_dir = os.path.join(INSTALL_DIR, site)
    dirs_to_create = (
        os.path.join(install_dir, 'releases'),
    )
    fab.sudo('mkdir -p {0}'.format(' '.join(dirs_to_create)))

    fab.puts("Upload project {0}".format(site))

    today = datetime.now().strftime('%Y%m%d-%H%M%S')
    commit_id = str(fab.local('git rev-parse {0}'.format(tag), True)).strip()
    current = "%s-%s" % (today, commit_id[:8])
    release_dir = os.path.join(INSTALL_DIR, site, 'releases')

    with cuisine.mode_sudo():
        cuisine.dir_ensure(release_dir)

    local_temp_dir = mkdtemp()
    archive = os.path.join(local_temp_dir, '{0}.tar.gz'.format(site))

    git_arch_cmd = "git archive --format=tar.gz -o {archive} {commit_id}:{project_dir}"
    fab.local(git_arch_cmd.format(archive=archive, commit_id=commit_id, project_dir=project_dir))

    with fab.lcd(local_temp_dir):
        remote_temp_dir = fab.run('mktemp -d')
        fab.put(archive, remote_temp_dir)
        with fab.cd(remote_temp_dir):
            fab.run("tar xzf {0}.tar.gz".format(site))
            fab.run("rm -f {0}.tar.gz".format(site))
        fab.sudo('chown -R root.root {0}'.format(remote_temp_dir))
        fab.sudo('chmod -R 755 {0}'.format(remote_temp_dir))
        fab.sudo("mv {tmp_dir} {release_dir}/{current}".format(release_dir=release_dir, current=current, tmp_dir=remote_temp_dir))
        fab.run('rm -rf {0}'.format(remote_temp_dir))
    fab.local('rm -rf {0}'.format(local_temp_dir))

    return current


@fab.task
def activate(release):
    """Activate release `release` code for project `project`."""
    project = fab.env.fabix['_current_project']

    fab.puts("Activating project {0} release {1}".format(project, release))
    with fab.cd(os.path.join(INSTALL_DIR, project)):
        fab.sudo("ln -nsf releases/{release} {project}".format(project=project, release=release))


@fab.task
def cleanup(keep=5):
    """Cleanup old releases for `site` keeping the `keep` most recent."""
    site = fab.env.fabix['_current_project']

    with fab.cd(os.path.join(INSTALL_DIR, site, 'releases')):
        files_to_remove = str(fab.run('ls -1')).split()
        if files_to_remove:
            cmd_args = ' '.join(files_to_remove[:-keep])
            fab.puts("Removing releases {0}".format(cmd_args))
            fab.sudo('rm -rf {0}'.format(cmd_args))
