import json
import os
from datetime import datetime, timezone
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

s3 = boto3.client("s3", config=Config(connect_timeout=5, read_timeout=10))

def lambda_handler(event, context):
    account_id = os.environ["AWS_ACCOUNT_ID"]

    try:
        raw = json.loads(
            s3.get_object(
                Bucket=os.environ["RAW_BUCKET"],
                Key="raw/earthquakes.json",
                ExpectedBucketOwner=account_id,
            )["Body"].read()
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            raise RuntimeError("Raw file not found — has the ingestor run yet?") from e
        raise

    quakes = []
    for f in raw["features"]:
        mag = f["properties"]["mag"]
        if not mag or mag <= 0:
            continue
        coords = f["geometry"]["coordinates"]
        quakes.append({
            "mag":   mag,
            "place": f["properties"]["place"] or "Unknown",
            "time":  f["properties"]["time"],
            "lat":   coords[1],
            "lng":   coords[0],
            "depth": coords[2],
        })

    try:
        s3.put_object(
            Bucket=os.environ["PROCESSED_BUCKET"],
            Key="earthquakes_processed.json",
            Body=json.dumps({"last_updated": datetime.now(timezone.utc).isoformat(), "earthquakes": quakes}),
            ContentType="application/json",
            ExpectedBucketOwner=account_id,
        )
    except ClientError as e:
        raise RuntimeError(f"Failed to write processed data to S3: {e}") from e

    return {"statusCode": 200}
