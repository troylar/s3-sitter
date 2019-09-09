import json
import boto3
from botocore.exceptions import ClientError
from fluentmetrics import FluentMetric


class s3_sitter:
    def __init__(self, **kwargs):
        self.buckets = []
        if kwargs.get('Buckets'):
            self.buckets = kwargs.get('Buckets').split(',')
        self.keys = kwargs.get('Keys', [])
        self.s3_c = boto3.client('s3')
        self.s3 = boto3.resource('s3')
        self.events = boto3.client('events')
        self.fm = FluentMetric(UseStreamId=False).with_namespace('S3Sitter')

    def is_bucket_accessible(self, bucket):
        try:
            self.s3.meta.client.head_bucket(Bucket=bucket)

        except ClientError:
            return False

        return True

    def is_key_accessible(self, bucket, key):
        try:
            self.s3.Object(bucket, key).load()
        except ClientError:
            return False

        return True

    def check_all_buckets(self):
        buckets = []
        for bucket in self.buckets:
            if not self.is_bucket_accessible(bucket):
                buckets.append(bucket)

        if len(buckets) > 0:
            entries = [{'DetailType': 'OneOrMoreS3BucketsInaccessible',
                        'Detail': {'Buckets': json.dumps(buckets)},
                        'Source': 's3_sitter'}]
            self.send_event(entries)
        print(len(buckets))
        self.fm.log(MetricName='InaccessibleBucketCount',
                    Value=len(buckets),
                    Unit='None')

    def check_all_keys(self):
        if self.keys == "":
            return
        keys = self.keys.split(',')
        for key in keys:
            b, k = self.parse_key(key)
            if not self.is_key_accessible(b, k):
                keys.append(key)

        if len(keys) > 0:
            entries = [{'DetailType': 'OneOrMoreS3KeysInaccessible',
                        'Detail': {'Keys': json.dumps(keys)},
                        'Source': 's3_sitter'}]
            self.send_event(entries)
        self.fm.log(MetricName='InaccessibleKeys',
                    Value=len(keys),
                    Unit='None')

    def send_event(self, entries):
        print('sending event')
        response = self.events.put_events(
            Entries=self.build_entries(entries))
        print(response)
        return response

    def build_entries(self, entries):
        cloudwatch_events = []
        for entry in entries:
            cloudwatch_events.append({
                'DetailType': entry['DetailType'],
                'Resources': entry['Resources'],
                'Source': entry['Source'],
                'Detail': json.dumps(entry['Detail'])
            })
        return cloudwatch_events

    def get_etag(self, full_key):
        b, k = self.parse_key(full_key)
        resp = self.s3_client.head_object(Bucket=b, Key=k)
        return resp('ETag')

    def parse_key(self, full_key):
        bucket = full_key.split('/')[0]
        key = '/'.join(full_key.split('/')[1:])
        return bucket, key
