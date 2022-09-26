"""Module containing classes that are used to find and delete resources"""

# Standard Library imports
from dataclasses import dataclass, field
from typing import Any, Collection, Optional, Union

# Local app imports
from delete_aws_resources_with_py import (
    create_boto3,
    logger,
    error_handler
)


@dataclass
class Resource:
    """
    Data-oriented class that takes in two instantiated boto3 objects [resource, client]
    and uses them to return VPC related information.
    :param boto_resource: (required) Instantiated boto3 resource
    :param boto_client: (required) Instantiated boto3 client
    """
    boto_resource: Any['boto_resource']
    boto_client: Any['boto_client']
    igw: Collection = field(init=False, repr=False)
    subnet: Collection = field(init=False, repr=False)
    route_table: Collection = field(init=False, repr=False)
    acl: Collection = field(init=False, repr=False)
    sgs: Collection = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.vpc_id:
            self.set_collection_data()

    @property
    def vpc_id(self) -> str:
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
        return self.boto_resource.Vpc(self.vpc_id)

    def set_collection_data(self) -> Optional[bool]:
        self.igw = self.current_vpc_resource.internet_gateways.all()
        _subnets = self.current_vpc_resource.subnets.all()
        self.subnet = [self.boto_resource.Subnet(subnet.id) for subnet in _subnets if subnet.default_for_az]
        self.route_table = self.current_vpc_resource.route_tables.all()
        self.acl = self.current_vpc_resource.network_acls.all()
        self.sgs = self.current_vpc_resource.security_groups.all()
        return True
