"""Module that contains pyfixture content to share"""
import json
# Standard Library imports
import os

# Third-party imports
import pytest
import boto3
from moto import mock_ec2

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
def get_resource_obj(ec2_client, ec2_resource):
    obj = Resource(boto_resource=ec2_resource, boto_client=ec2_client,
                   region='us-east-1')
    return obj


@pytest.fixture
def egress_rule():
    with open('tests/json_files/egress_sg_rule.json', 'rb') as f:
        return json.load(f)