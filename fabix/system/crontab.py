# coding: utf-8
import fabric.api as fab
import cuisine


def install(filename, user="root", append=False):
    """
    Installs crontab from a given cronfile
    """
    new_crontab = fab.run("mktemp fabixcron.XXXX")
    cuisine.file_upload(new_crontab, filename)
    if append is True:
        # When user have no crontab, then crontab command returns 1 error code
        with fab.settings(warn_only=True):
            fab.sudo("crontab -u {} -l 2> /dev/null | awk '!x[$0]++{{print $0}}' >> {}".format(user, new_crontab))
    fab.sudo("crontab -u {} {}".format(user, new_crontab))
