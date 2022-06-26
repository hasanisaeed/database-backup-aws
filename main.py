import logging
import argparse
import configparser
import datetime
import subprocess
import gzip
import os
from time import sleep
import boto3


def upload_to_s3(file_full_path, dest_file, manager_config):
    """
    Upload a file to an MinIO S3 bucket.
    """
    session = boto3.session.Session()

    # config connection requirements
    s3_client = session.client(
        service_name='s3',
        aws_access_key_id=manager_config.get('AWS_KEY_ID'),
        aws_secret_access_key=manager_config.get('AWS_ACCESS_KEY'),
        endpoint_url=manager_config.get('AWS_ENDPOINT'),
    )

    try:
        s3_client.upload_file(file_full_path,
                              manager_config.get('AWS_BUCKET_NAME'),
                              manager_config.get('AWS_BUCKET_PATH') + dest_file)
        os.remove(file_full_path)
    except boto3.exceptions.S3UploadFailedError as exc:
        exit(1)


def compress_to_gz(src_file):
    gz_file = "%s.gz" % str(src_file)

    with open(src_file, 'rb') as f_in:
        with gzip.open(gz_file, 'wb') as f_out:
            for line in f_in:
                f_out.write(line)
    return gz_file


def backup_from_database(host, database_name, port, user, password, dest_file):
    """
    Backup from database
    """
    try:
            process = subprocess.Popen(
                [
                 'pg_dump',
                 '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, database_name),
                 '-Fc',
                 '-f', dest_file,
                 '-v'],
                stdout=subprocess.PIPE
            )
            output = process.communicate()[0]
            if int(process.returncode) != 0:
                exit(1)
            return output
    except Exception as e:
            exit(1)


def main():
    # config logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    args_parser = argparse.ArgumentParser(description='Postgres database management')
    args_parser.add_argument("--action",
                             metavar="action",
                             choices=['backup', 'restore'],
                             required=True)

    args_parser.add_argument("--configfile",
                             required=True,
                             help="Database configuration file")


    args = args_parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.configfile) 

    project_name = config.get('Project', 'project_name')

    postgres_host = config.get('postgresql', 'host')
    postgres_port = config.get('postgresql', 'port')
    postgres_db = config.get('postgresql', 'db')
    postgres_user = config.get('postgresql', 'user')
    postgres_password = config.get('postgresql', 'password')

    timestr = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    filename = 'backup-%s.dump' % timestr
    filename_compressed = '%s.gz' % filename

    local_storage_path = config.get('local_storage', 'path', fallback='./backups/')

    aws_bucket_name = config.get('S3', 'bucket_name')
    aws_key_id = config.get('S3', 'key_id')
    aws_access_key = config.get('S3', 'access_key')
    aws_endpoint = config.get('S3', 'endpoint')

    manager_config = {
        'AWS_BUCKET_NAME': aws_bucket_name,
        'AWS_BUCKET_PATH': '%s/%s'%(project_name, postgres_db),
        'BACKUP_PATH': '%s/backup/' % os.path.dirname(os.path.realpath(__file__)),
        'LOCAL_BACKUP_PATH': local_storage_path,
        'AWS_KEY_ID': aws_key_id,
        'AWS_ACCESS_KEY': aws_access_key,
        'AWS_ENDPOINT' : aws_endpoint
    }

    local_file_path = '%s%s' % (manager_config.get('BACKUP_PATH'), filename)

    logger.info('Backing up %s database to %s' % (postgres_db, local_file_path))
    
    interval = int(config.get('Project', 'interval'))

    if args.action == "backup":
        while True:
            result = backup_from_database(postgres_host, 
                                        postgres_db,
                                        postgres_port,
                                        postgres_user,
                                        postgres_password,
                                        local_file_path)

            comp_file = compress_to_gz(local_file_path)

            logger.info('Uploading %s to MinIO S3...' % comp_file)

            upload_to_s3(comp_file, filename_compressed, manager_config)

            logger.info("Uploaded to %s" % filename_compressed)
            sleep(interval)

if __name__ == '__main__':
    main()