"""Module containing the main script to run"""

# !/usr/bin/env python

# Local app imports
# from get_resources import GetRegions
# from select_options import SetArgsAndObjects
from delete_aws_resources_with_py import (
    AlterResources,
    create_logger

)

#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'

logger = create_logger()
skip_region_list = ["us-east-1", "us-west-2"]
# regionClient = boto3.client('ec2')
# regionResources = GetRegions(regionClient)
# regions = regionResources.getRegions()


if __name__ == "__main__":

    logger.info("[!] Attempting to get resources")
    get_regions = AlterResources('ec2', skip_region_list)
    get_regions.call_vpc()

    # outArgs = getArgs()
    # for region in regions:
    #     try:
    #         vpcClient = boto3.client('ec2', region_name=region)
    #         ec2 = boto3.resource('ec2', region_name=region)
    #         optionSet = SetArgsAndObjects(vpcClient, ec2, region)
    #
    #         if outArgs.sanitize_option == "all":
    #             optionSet.allOptions()
    #         elif outArgs.sanitize_option == "deleteonly":
    #             optionSet.deleteResourcesOption()
    #         elif outArgs.sanitize_option == "modifyonly":
    #             optionSet.modifyResourceOption()
    #         else:
    #             logger.error("[-] The option provided was not found, please try again (--help for more info)")
    #     except Exception as e:
    #         logger.error("[-] Failed to create variables with error: %s", e)
