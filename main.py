"""Module containing the main script to run"""

# !/usr/bin/env python

# Local app imports
from get_resources import GetRegions
from select_options import SetArgsAndObjects
from utils import (
    getArgs,
    create_logger,
    create_boto3_resource,
    create_boto3_client
)

#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'

logger = create_logger()
regionClient = boto3.client('ec2')
regionResources = GetRegions(regionClient)
regions = regionResources.getRegions()


#  Main Function
def main():
    outArgs = getArgs()
    for region in regions:
        try:
            vpcClient = boto3.client('ec2', region_name=region)
            ec2 = boto3.resource('ec2', region_name=region)
            optionSet = SetArgsAndObjects(vpcClient, ec2, region)

            if outArgs.sanitize_option == "all":
                optionSet.allOptions()
            elif outArgs.sanitize_option == "deleteonly":
                optionSet.deleteResourcesOption()
            elif outArgs.sanitize_option == "modifyonly":
                optionSet.modifyResourceOption()
            else:
                logger.error("[-] The option provided was not found, please try again (--help for more info)")
        except Exception as e:
            logger.error("[-] Failed to create variables with error: %s", e)


if __name__ == "__main__":
    main()
