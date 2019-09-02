import json
import boto3
from botocore.exceptions import ClientError


class s3_sitter:
    def __init__(self, **kwargs):
        self.buckets = kwargs.get('Buckets', [])
        self.keys = kwargs.get('Keys', [])
        self.s3 = boto3.resource('s3')
        self.events = boto3.client('events')

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

    def check_all_keys(self):
        if len(self.keys) == 0:
            return
        keys = []
        for key in self.keys:
            if not self.is_key_accessible(key['Bucket'], key['Key']):
                keys.append(key)

        if len(keys) > 0:
            entries = [{'DetailType': 'OneOrMoreS3KeysInaccessible',
                        'Detail': {'Keys': json.dumps(keys)},
                        'Source': 's3_sitter'}]
        self.send_event(entries)

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
                'Source': entry['Source'],
                'Detail': json.dumps(entry['Detail'])
            })
        return cloudwatch_events
