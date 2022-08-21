"""Module containing classes that are used to find and delete resources"""

# Standard Library imports
import os
from dataclasses import dataclass
import json

# Third-party imports
from botocore.exceptions import ClientError

# Local app imports
from delete_aws_resources_with_py import (
    create_boto3_client,
    create_boto3_resource,
    create_logger,
    getArgs
)

logger = create_logger()


@dataclass
class Resources:
    resource: str
    skip_region_list: list

    def __post_init__(self):
        self.region_list = self.get_regions()

    def get_regions(self) -> list:
        """
        Will generate a list of regions to take action on
        :return: List containing the regions to delete resources from
        :raise: AWS API "Boto3" ClientErrors
        """
        region_list = []
        try:
            get_region_object = create_boto3_client(self.resource).describe_regions()
            for region in get_region_object['Regions']:
                if region['RegionName'] in self.skip_region_list:
                    region_list.append(region['RegionName'])
            return region_list
        except ClientError as e:
            logger.error("[-] Failed to retrieve region object from AWS with error: %s", e)

    def get_vpcs(self, current_region: str) -> list:
        vpc_list = []
        try:
            vpcs = create_boto3_client(self.resource, region=current_region).describe_vpcs(
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
                vpc_list.append(vpc['VpcId'])
            return vpc_list
        except ClientError as e:
            logger.error("[-] Failed to call the describe_vpc method with error: %s", e)


@dataclass
class AlterResources(Resources):
    args: str
    current_vpc: list = None
    boto_resource: str = None
    current_region: str = None

    def call_methods(self):
        for region in self.region_list:
            try:
                self.current_region = region
                self.current_vpc = self.get_vpcs(current_region=region)
                self.boto_resource = create_boto3_resource(self.resource, region=region)
            except ClientError as e:
                logger.error("[-] Failed to get boto_resource with error: %s", e)
            except Exception as e:
                logger.error("[-] Failed to get VPC data from method with error: %s", e)
            else:
                print(self.current_region, self.current_vpc)
                print(self.args)

