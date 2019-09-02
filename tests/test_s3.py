import boto3
import mock
from moto import mock_s3, mock_events
from s3_sitter import s3_sitter


class Tests:
    def gen_data(self):
        self.buckets = ["bucket1", "bucket2"]
        self.keys = [{"Bucket": "bucket1", "Key": "key1"},
                     {"Bucket": "bucket2", "Key": "key2:"}]

    def test_can_pass_buckets(self):
        self.gen_data()
        sitter = s3_sitter(Buckets=self.buckets)
        assert len(sitter.buckets) == 2

    def test_can_pass_keys(self):
        self.gen_data()
        sitter = s3_sitter(Keys=self.keys)
        assert len(sitter.keys) == 2

    def test_can_check_if_missing_bucket_accessible(self):
        self.gen_data()
        sitter = s3_sitter()
        assert not sitter.is_bucket_accessible(self.buckets[0])

    def test_can_check_if_existing_bucket_accessible(self):
        self.gen_data()
        sitter = s3_sitter()
        assert not sitter.is_bucket_accessible(self.buckets[1])

    @mock_s3
    def test_can_check_if_existing_key_exists(self):
        self.gen_data()
        sitter = s3_sitter()
        s3 = boto3.client('s3', region_name='us-east-1')
        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket=self.buckets[0])
        s3.put_object(Bucket=self.keys[0]['Bucket'],
                      Key=self.keys[0]['Key'], Body="test")
        assert sitter.is_key_accessible(self.keys[0]['Bucket'],
                                        self.keys[0]['Key'])

    @mock_s3
    def test_missing_key_is_not_accessible(self):
        self.gen_data()
        sitter = s3_sitter()
        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket=self.keys[0]['Bucket'])
        assert not sitter.is_key_accessible(self.keys[0]['Bucket'],
                                            self.keys[0]['Key'])

    def test_entries_built_correctly(self):
        sitter = s3_sitter()
        entries = [
            {'DetailType': 'BucketError',
             'Resources': ['bucket1', 'bucket2'],
             'Source': 'TestSource'}
            ]
        resp = sitter.build_entries(entries)
        assert resp == [{'DetailType': 'BucketError',
                         'Resources': ['bucket1', 'bucket2'],
                         'Source': 'TestSource'}]

    @mock_events
    def test_events_sent_successfully(self):
        sitter = s3_sitter()
        entries = [
            {'DetailType': 'BucketError',
             'Resources': ['bucket1', 'bucket2'],
             'Source': 'TestSource'}
            ]
        resp = sitter.send_event(entries)
        assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

    @mock_s3
    @mock_events
    @mock.patch('s3_sitter.s3_sitter.send_event')
    def test_missing_bucket_sends_event(self, send_event_mock):
        sitter = s3_sitter(Buckets=['bucket1', 'bucket2'])
        sitter.check_all_buckets()
        send_event_mock.assert_called_with([{'DetailType': 'InaccessibleS3Bucket', 'Resources': ['bucket1', 'bucket2'], 'Source': 'aws.s3'}])

    @mock_s3
    @mock_events
    @mock.patch('s3_sitter.s3_sitter.send_event')
    def test_missing_key_sends_event(self, send_event_mock):
        self.gen_data()
        sitter = s3_sitter(Keys=self.keys)
        sitter.check_all_keys()
        send_event_mock.assert_called_with([{'DetailType': 'InaccessibleS3Key', 'Resources': [{'Bucket': 'bucket1', 'Key': 'key1'}, {'Bucket': 'bucket2', 'Key': 'key2:'}], 'Source': 's3_sitter'}])
