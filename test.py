import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

auth = BotoAWSRequestsAuth(aws_host='issues-ext.amazon.com',
                           aws_region='us-east-1',
                           aws_service='sim')
data = {
    "title": "Fake Title",
    "description": "Fake Description",
    "assignedFolder": "0f035a4b-3c64-49f1-93d4-fba944387631"
  }

response = requests.post('https://issues-ext.amazon.com/issues',
                        data=data,
                        auth=auth)
print(response.content)
