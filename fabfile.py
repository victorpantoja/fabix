import boto

boto.config.load_from_path('boto.cfg')

import fabix.aws.s3
import fabric.api as fab


filename = "/Users/rcmachado/Developer/quatix/euatleta/src/website/website/media/img/map-image.png"


@fab.task
def teste():
    conn = boto.connect_s3()
    bucket = conn.get_bucket('euatleta')

    fabix.aws.s3.upload_file(bucket, 'teste.png', filename)
