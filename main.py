"""Module containing the main script to run"""

# !/usr/bin/env python

# Local app imports
from delete_aws_resources_with_py import (
    create_logger,
    AlterResources,
    getArgs
)

#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'

logger = create_logger()
SKIP_REGIONS = ["us-east-1", "us-west-2"]


if __name__ == "__main__":
    args = getArgs()
    try:
        get_regions = AlterResources(resource='ec2', skip_region_list=SKIP_REGIONS, args=args)
    except Exception as e:
        logger.error("[-] Failed to instantiate the object with error: %s", e)
    else:
        logger.info("[!] Attempting to obtain region/vpc data & perform action='%s' on default resources", args.sanitize_option)
        get_regions.call_methods()


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
