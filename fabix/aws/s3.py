import os

import boto
from boto.utils import compute_md5
from fabric.decorators import task
from fabric.utils import puts


def upload_file(bucket, key_name, file_path, remote_prefix=None, policy='public-read', metadata=None):
    if not metadata:
        metadata = {}

    if remote_prefix:
        key_name = '{0}/{1}'.format(remote_prefix, key_name)

    fd = open(file_path)
    md5 = compute_md5(fd)
    fd.close()

    current_md5 = None
    current_key = bucket.lookup(key_name)
    if current_key:
        current_md5 = current_key.get_metadata('fabix-md5')
        if current_md5 == md5[0]:
            for k, v in metadata.iteritems():
                current_key.set_metadata(k, v)
            puts("Skip file {0}".format(file_path))
            return current_key

    key = bucket.new_key(key_name)

    for k, v in metadata.iteritems():
        key.set_metadata(k, v)

    key.set_metadata('fabix-md5', md5[0])

    puts("Upload file {0}".format(file_path))
    key.set_contents_from_filename(file_path, md5=md5, policy=policy)
    return key


def get_key_name(local_path, fullpath):
    key_name = fullpath[len(local_path):]
    l = key_name.split(os.sep)
    key_name = '/'.join(l)
    return key_name.lstrip('/')


@task
def sync_dir_up(bucket_name, local_path, remote_prefix=None, metadata=None):
    puts("Sync directory {0} with bucket {1}".format(bucket_name, local_path))
    conn = boto.connect_s3()
    bucket = conn.get_bucket(bucket_name)

    for root, dirs, files in os.walk(local_path):
        for fname in files:
            file_path = os.path.join(root, fname)
            key_name = get_key_name(local_path, file_path)

            upload_file(bucket, key_name, file_path, remote_prefix=remote_prefix, metadata=metadata)
