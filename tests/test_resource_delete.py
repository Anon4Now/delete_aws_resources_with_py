"""Module containing tests for Delete class"""

# Local App imports
from delete_aws_resources_with_py.resource_delete import Delete
from delete_aws_resources_with_py.default_resources import Resource


def test_delete_class(get_resource_obj):
    del_res = Delete(get_resource_obj)
    assert del_res.delete_resources() is True


def test_custom_vpc(ec2_client, ec2_resource):
    default_vpc = ec2_client.describe_vpcs()
    for el in default_vpc['Vpcs']:
        rtb = ec2_client.create_route_table(
            VpcId=el['VpcId']
        )
        print(ec2_client.describe_route_tables())
        sg = ec2_client.create_security_group(
            Description='fake sg for testing',
            GroupName='sg-12345667',
            VpcId=el['VpcId']
        )

        nacl = ec2_client.create_network_acl(
            VpcId=el['VpcId'])
    #
    # # vpc_id = ec2_client.create_vpc(
    # #     CidrBlock='10.0.0.0/16',
    # #     AmazonProvidedIpv6CidrBlock=True,
    # #     InstanceTenancy='default',
    # #     Ipv6CidrBlockNetworkBorderGroup='string'
    # # )
    # # rtb = ec2_client.create_route_table(
    # #     VpcId=vpc_id['Vpc']['VpcId']
    # # )
    # # sg = ec2_client.create_security_group(
    # #     Description='fake sg for testing',
    # #     GroupName='sg-12345667',
    # #     VpcId=vpc_id['Vpc']['VpcId']
    # # )
    # #
    # # nacl = ec2_client.create_network_acl(
    # #     VpcId=vpc_id['Vpc']['VpcId']
    # # )
    # TODO: THERE IS A BUG IN THE ASSOCIATED_ATTR VAR - RUN TEST TO SEE (NEED TO DELETE NON-DEFAULT RTB)
    obj = Resource(boto_resource=ec2_resource, boto_client=ec2_client,
                   region='us-east-1')
    for route_table in obj.route_table:
        print(route_table)
        associated_attribute = [routeTable.associations_attribute for routeTable in
                                obj.route_table]
        print(associated_attribute)
    del_res = Delete(obj)
    assert del_res.delete_resources() is True