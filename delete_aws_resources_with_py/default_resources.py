"""Module containing classes that are used to find and delete resources"""

# Standard Library imports
from dataclasses import dataclass

# Local app imports
from delete_aws_resources_with_py import (
    create_boto3,
    create_logger,
    error_handler
)

logger = create_logger()


@dataclass
class Resource:
    resource: str = None
    region: str = None

    # TODO: BUILD IN SAFETY CHECKS BEFORE INSTANTIATING BOTO
    def __post_init__(self) -> None:
        self.boto_resource = create_boto3(service=self.resource, boto_type="boto_resource", region=self.region)
        self.boto_client = create_boto3(service=self.resource, boto_type="boto_client", region=self.region)
        self.vpc_id = self.get_vpcs()
        if self.vpc_id:
            self.current_vpc_resource = self.boto_resource.Vpc(self.vpc_id)
            self.igw = self.current_vpc_resource.internet_gateways.all()
            subnets = self.current_vpc_resource.subnets.all()
            self.default_subnets = [self.boto_resource.Subnet(subnet.id) for subnet in subnets if subnet.default_for_az]
            self.route_tables = self.current_vpc_resource.route_tables.all()
            self.acls = self.current_vpc_resource.network_acls.all()
            self.sgs = self.current_vpc_resource.security_groups.all()

    @error_handler
    def get_vpcs(self) -> str:
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