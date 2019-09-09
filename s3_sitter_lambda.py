import json
from s3_sitter import s3_sitter


def handler(event, context):
    buckets = "aws-price-magician-data"
    keys_j = [{"Bucket": "aws-price-magician-data", "Key": "AWSGlue/location=AWS GovCloud (US)/AWSGlue.csv"}]
    sitter = s3_sitter(Buckets=buckets, Keys=keys_j)
    sitter.check_all_buckets()
    sitter.check_all_keys()
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
