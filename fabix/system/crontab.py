# coding: utf-8
import fabric.api as fab
import cuisine


def install(filename, user="root"):
    """
    Installs crontab from a given cronfile
    """
    tmp_file = fab.run("mktemp fabixcron.XXXX")
    cuisine.file_upload(tmp_file, filename)
    fab.sudo("crontab -u{} {}".format(user, tmp_file))
