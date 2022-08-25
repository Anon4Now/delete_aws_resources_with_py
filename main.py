"""Module containing the main script to run"""

# !/usr/bin/env python

# Local app imports
from delete_aws_resources_with_py import (
    create_logger,
    getArgs
)

#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'

logger = create_logger()
SKIP_REGIONS = ["us-east-1", "us-west-2"]


def main():
    args = getArgs()
    

if __name__ == "__main__":
    main()

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
