"""Module containing tests for Resource class"""

# Standard Library imports
import os

# Third-party imports
import pytest
import boto3
from moto import mock_ec2, mock_s3

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


def test_resource_class_vpc_present(ec2_client, ec2_resource) -> None:
    obj = Resource(boto_resource=ec2_resource, boto_client=ec2_client,
                   region='us-east-1')

    assert obj.vpc_id is not None
    assert obj.igw is not None
    assert obj.subnet is not None
    assert obj.route_table is not None
    assert obj.acl is not None
    assert obj.sgs is not None