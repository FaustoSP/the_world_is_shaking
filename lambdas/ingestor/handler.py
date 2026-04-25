import os
import urllib.request
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"

s3 = boto3.client("s3", config=Config(connect_timeout=5, read_timeout=10))

def lambda_handler(event, context):
    data = urllib.request.urlopen(USGS_URL, timeout=10).read()

    try:
        s3.put_object(
            # This variable is set by Terraform in lambda.tf
            Bucket=os.environ["RAW_BUCKET"],
            Key="raw/earthquakes.json",
            Body=data,
            ContentType="application/json",
            ExpectedBucketOwner=os.environ["AWS_ACCOUNT_ID"],
        )
    except ClientError as e:
        raise RuntimeError(f"Failed to write raw data to S3: {e}") from e

    return {"statusCode": 200}
