"""Module containing classes that are used to find and delete resources"""

# Standard Library imports
import os
from dataclasses import dataclass
import json

# Third-party imports
from botocore.exceptions import ClientError

# Local app imports
from utils import (
    create_logger,
    create_boto3_client,
    create_boto3_resource,
    AWS_ACCESS_KEY,
    AWS_SECRET_KEY
)

logger = create_logger()


@dataclass
class DefaultResources:
    region_list: list
    vpc_list: list
    skip_regions: list = None

    def __init__(self):
        self.region_list = self.get_regions()
        self.skip_regions = ["us-east-1", "us-west-2"]

    def get_regions(self) -> list:
        """
        Will generate a list of regions to take action on
        :return: List containing the regions to delete resources from
        :raise: AWS API "Boto3" ClientErrors
        """
        try:
            get_region_object = create_boto3_client('ec2', region=None, access_key=AWS_ACCESS_KEY, secret_key=AWS_SECRET_KEY).describe_regions()
            print("DELETE ME AFTER USE IN DATACLASS", get_region_object)
            #  json data parsing
            jsonStr = json.dumps(get_region_object)
            print(jsonStr)
            response = json.loads(jsonStr)
            print(response)
            regionStr = json.dumps(response['Regions'])
            print(regionStr)
            regions = json.loads(regionStr)
            print(regions)
        except ClientError as e:
            logger.error("[-] Failed to retrieve region object from AWS with error: %s", e)


class GetResources(DefaultResources):
    pass


class DeleteResources(DefaultResources):
    pass
