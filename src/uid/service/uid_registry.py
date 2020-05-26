#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This is the module."""
import io
import os
import logging

from minio import Minio

from minio.error import NoSuchKey

MINIO_URL        = os.environ.get('MINIO_URL')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
AUTH_BUCKET_NAME = os.environ.get('MINIO_AUTH_BUCKET', 'auth')


def uid_register_job(job_id, metadata=None):
    """
    Register new job

    Args:
        job_id: id of the job to be registered
        metadata: dictionary of metadata(if any)

    Returns: None

    Notes:
        ValueError exception will be raised if
        job has been previously registered

    """

    minioClient = Minio(MINIO_URL,
                        access_key=MINIO_ACCESS_KEY,
                        secret_key=MINIO_SECRET_KEY,
                        secure=False)

    if not minioClient.bucket_exists(AUTH_BUCKET_NAME):
        minioClient.make_bucket(AUTH_BUCKET_NAME)

    object_name = str(job_id)

    # look for previous registration
    try:
        minioClient.stat_object(AUTH_BUCKET_NAME, object_name)
        logging.error(F"Job id {object_name} has been registered previously")
        raise ValueError
    except NoSuchKey as err:
        pass

    minioClient.put_object(AUTH_BUCKET_NAME, object_name,
                           data=io.BytesIO(),
                           length=0,
                           metadata=metadata)


def uid_void_job(job_id):
    """
    Void previously registered job

    Args:
        job_id: job identifier

    Returns: None

    Notes:
        If job identifier is not found only warning will logged

    """
    minioClient = Minio(MINIO_URL,
                        access_key=MINIO_ACCESS_KEY,
                        secret_key=MINIO_SECRET_KEY,
                        secure=False)

    object_name = str(job_id)

    # look for previous registration
    try:
        minioClient.stat_object(AUTH_BUCKET_NAME, object_name)
    except NoSuchKey as err:
        logging.warning(F"Received request to delete unknown job {object_name}")

    minioClient.remove_object(AUTH_BUCKET_NAME, object_name)


def uid_validate_job(job_id):
    """
    Validate job

    Args:
        job_id: job identifier

    Returns:
        Job meta_data dictionary if job identifier is valid
        None otherwise

    """

    minioClient = Minio(MINIO_URL,
                        access_key=MINIO_ACCESS_KEY,
                        secret_key=MINIO_SECRET_KEY,
                        secure=False)

    object_name = str(job_id)

    try:
        obj = minioClient.stat_object(AUTH_BUCKET_NAME, object_name)
        metadata = {"created_dt": obj.last_modified, **obj.metadata}
    except NoSuchKey as err:
        metadata = None

    return metadata

def uid_register_job1(job_id, info=""):
    minioClient = Minio(MINIO_URL,
                        access_key=MINIO_ACCESS_KEY,
                        secret_key=MINIO_SECRET_KEY,
                        secure=False)

    if not minioClient.bucket_exists(AUTH_BUCKET_NAME):
        minioClient.make_bucket(AUTH_BUCKET_NAME)

    object_name = str(job_id)

    # look for previous registration
    try:
        minioClient.stat_object(AUTH_BUCKET_NAME, object_name)
        logging.error(F"Job id {object_name} has been registered previously")
        raise ValueError
    except NoSuchKey as err:
        pass

    object_data = info.encode("utf-8")
    minioClient.put_object(AUTH_BUCKET_NAME, object_name,
                           data=io.BytesIO(object_data),
                           length=len(object_data))