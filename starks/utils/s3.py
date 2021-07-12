import logging

import boto3
from botocore.exceptions import ClientError


def sign_get_url(obj_key, bucket_name, expiration_sec=(60 * 60)):
    s3 = boto3.client("s3")
    try:
        response = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": obj_key,
            },
            ExpiresIn=expiration_sec,
        )
    except ClientError as e:
        logging.error(e)
        return None
