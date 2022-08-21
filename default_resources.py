"""Module containing classes that are used to find and delete resources"""

# Standard Library imports
from dataclasses import dataclass

# Third-party imports
from botocore.exceptions import ClientError

# Local app imports
from utils import (
    create_logger,
    create_boto3_client,
    create_boto3_resource
)

logger = create_logger()


@dataclass
class DefaultResources:
    region_list: list
    vpc_list: list
    skip_regions: list = None

    def __init__(self):
        pass

    def get_regions(self) -> list:
        """
        Will generate a list of regions to take action on
        :return: List containing the regions to delete resources from
        :raise: AWS API "Boto3" ClientErrors
        """
        try:
            get_regions = create_boto3_client('ec2').describe_regions()
            print("DELETE ME AFTER USE IN DATACLASS", get_regions)
        except ClientError as e:
            logger.error("[-] Failed to retrieve region object from AWS with error: %s", e)


class GetResources(DefaultResources):
    pass


class DeleteResources(DefaultResources):
    pass
