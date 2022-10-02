"""Module containing tests for Resource class"""

# Local App imports
from delete_aws_resources_with_py.default_resources import Resource


def test_resource_class_vpc_present(ec2_client, ec2_resource) -> None:
    obj = Resource(boto_resource=ec2_resource, boto_client=ec2_client,
                   region='us-east-1')

    assert obj.vpc_id is not None
    assert obj.igw is not None
    assert obj.subnet is not None
    assert obj.route_table is not None
    assert obj.acl is not None
    assert obj.sgs is not None
