import os
import urllib.request
import boto3

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"

def lambda_handler(event, context):
    data = urllib.request.urlopen(USGS_URL).read()

    boto3.client("s3").put_object(
        # This variable is set by Terraform in lambda.tf
        Bucket=os.environ["RAW_BUCKET"],
        Key="raw/earthquakes.json",
        Body=data,
        ContentType="application/json",
    )

    return {"statusCode": 200}
