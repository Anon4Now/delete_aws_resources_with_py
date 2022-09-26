"""Module containing classes that are used to find and delete resources"""

# Standard Library imports
from dataclasses import dataclass, field
from typing import Any, Collection, Optional, Union

# Third-party imports
from botocore.exceptions import ClientError

# Local App imports
from delete_aws_resources_with_py.errors import NoDefaultVpcFoundError


@dataclass
class Resource:
    """
    Data-oriented class that takes in two instantiated boto3 objects [resource, client]
    and a region to return VPC related information.
    :param boto_resource: (required) Instantiated boto3 resource
    :param boto_client: (required) Instantiated boto3 client
    """
    boto_resource: Any['boto_resource']
    boto_client: Any['boto_client']
    region: str
    igw: Collection = field(init=False, repr=False)
    subnet: Collection = field(init=False, repr=False)
    route_table: Collection = field(init=False, repr=False)
    acl: Collection = field(init=False, repr=False)
    sgs: Collection = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Populate the class attrs with data if a default VPC is found"""
        if self.vpc_id:
            self.set_collection_data()
        else:
            raise NoDefaultVpcFoundError

    @property
    def vpc_id(self) -> str:
        """Property that will provide the string value of the VPC associated with the region"""
        vpcs = self.boto_client.describe_vpcs(
            Filters=[
                {
                    'Name': 'isDefault',
                    'Values': [
                        'true',

                    ],
                },
            ]
        )

        # add vpc's to instance attribute
        for vpc in vpcs['Vpcs']:
            return vpc['VpcId']

    @property
    def current_vpc_resource(self) -> Any['boto_resource']:
        """
        Property that will provide the resource content
        tied to the current VPC in the current region.
        :return An instantiated boto3 resource for the current VPC
        """
        return self.boto_resource.Vpc(self.vpc_id)

    def set_collection_data(self) -> Optional[bool]:
        """
        This method is used to populate the class attr collections with data.
        It makes calls to the all() method on the resource items which updates
        the attrs with collections of data.

        :return: A boolean result if all calls were made successfully (True=success)
        """
        try:
            self.igw = self.current_vpc_resource.internet_gateways.all()
            _subnets = self.current_vpc_resource.subnets.all()
            self.subnet = [self.boto_resource.Subnet(subnet.id) for subnet in _subnets if subnet.default_for_az]
            self.route_table = self.current_vpc_resource.route_tables.all()
            self.acl = self.current_vpc_resource.network_acls.all()
            self.sgs = self.current_vpc_resource.security_groups.all()
        except ClientError:
            raise
        else:
            return True
