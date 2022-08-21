"""Module containing classes that are used to find and delete resources"""

# Standard Library imports
import os
from dataclasses import dataclass
import json

# Third-party imports
from botocore.exceptions import ClientError

# Local app imports
from delete_aws_resources_with_py import (
    create_logger,
    create_boto3_client,
    create_boto3_resource
)

logger = create_logger()


# @dataclass
# class DefaultResources:
#     region_list: list
#     vpc_list: list
#     skip_regions: list = None
#
#     def __post_init__(self):
#         self.skip_regions = ["us-east-1", "us-west-2"]
#         self.region_list = self.get_regions()
#
#     def get_regions(self) -> list:
#         """
#         Will generate a list of regions to take action on
#         :return: List containing the regions to delete resources from
#         :raise: AWS API "Boto3" ClientErrors
#         """
#         region_list = []
#         try:
#             get_region_object = create_boto3_client('ec2').describe_regions()
#             for region in get_region_object['Regions']:
#                 if region['RegionName'] in self.skip_regions:
#                     region_list.append(region['RegionName'])
#             return region_list
#         except ClientError as e:
#             logger.error("[-] Failed to retrieve region object from AWS with error: %s", e)

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

    def get_vpcs(self, current_region) -> list:
        vpc_list = []
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
        print(vpc_list)
        return vpc_list


class AlterResources(Resources):
    pass
