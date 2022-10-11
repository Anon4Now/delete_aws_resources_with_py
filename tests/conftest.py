"""Module that contains pyfixture content to share"""
# Standard Library imports
import os
import json
from collections import namedtuple

# Third-party imports
import pytest
import boto3
from moto import mock_ec2, mock_ssm

# Local App imports
from delete_aws_resources_with_py.default_resources import Resource


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope='function')
def ec2_client(aws_credentials):
    with mock_ec2():
        conn = boto3.client("ec2", region_name="us-east-1")
        yield conn


@pytest.fixture(scope='function')
def ec2_resource(aws_credentials):
    with mock_ec2():
        conn = boto3.resource("ec2", region_name="us-east-1")
        yield conn


@pytest.fixture
def ssm_client(aws_credentials):
    with mock_ssm():
        conn = boto3.client("ssm", region_name="us-east-1")
        yield conn


@pytest.fixture
def get_resource_obj(ec2_client, ec2_resource):
    obj = Resource(boto_resource=ec2_resource, boto_client=ec2_client,
                   region='us-east-1')
    return obj


@pytest.fixture
def sg_egress_ingress_rule():
    with open('tests/json_files/egress_sg_rule.json', 'rb') as f:
        return json.load(f)


class MockResponses:
    def __init__(self):
        self.client = {}
        self.resource = {}

    def get_service_setting(self, *args, **kwargs):
        return {
            'ServiceSetting': {
                'SettingValue': 'Enable'
            }
        }

    def update_service_setting(self, *args, **kwargs):
        return {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            }
        }

    def describe_security_group_rules(self, *args, **kwargs):
        return 'sgr-0f5d697d6bde6f9da'

    def revoke_security_group_ingress(self, *args, **kwargs):
        return True

    def revoke_security_group_egress(self, *args, **kwargs):
        return True


@pytest.fixture
def fake_boto_client():
    return MockResponses()


class MockResource:
    def __init__(self, boto_client, boto_resource):
        self.boto_client = boto_client
        self.boto_resource = boto_resource
        self.region = 'us-east-1'
        security_groupsCollection = namedtuple('security_groupsCollection', ['id', 'group_name'])
        self.sgs = security_groupsCollection(sg_egress_ingress_rule, 'default')


@pytest.fixture
def fake_resource_obj(fake_boto_client):
    return MockResource(fake_boto_client, fake_boto_client)
