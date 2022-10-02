"""Module containing the main script to run"""

# !/usr/bin/env python

# Local app imports
from delete_aws_resources_with_py.utils import (
    logger,
    create_boto3,
    error_handler,
    getArgs,
    SKIP_REGION_LIST
)
from delete_aws_resources_with_py.resource_updates import (
    Delete,
    Update
)
from delete_aws_resources_with_py.default_resources import Resource


#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'


@error_handler
def main():
    args = getArgs()
    get_region_object = create_boto3(service='ec2', boto_type='boto_client').describe_regions()
    region_list = [x['RegionName'] for x in get_region_object['Regions'] if
                   x['RegionName'] in SKIP_REGION_LIST]
    for current_region in region_list:
        ssm_client = create_boto3(service='ssm', boto_type='boto_client', region=current_region)
        boto_resource = create_boto3(service='ec2', boto_type="boto_resource", region=current_region)
        boto_client = create_boto3(service='ec2', boto_type="boto_client", region=current_region)
        obj = Resource(boto_resource=boto_resource, boto_client=boto_client,
                       region=current_region)  # instantiate the Resource object
        if args.sanitize_option not in ['delete', 'modify']:  # validate cmd line arg
            logger.error("[-] Entered an incorrect option, use -h or --help for more information")
            break
        elif not obj.vpc_id:
            logger.info("[!] Region: '%s' does not have a default VPC, continuing", current_region)
            continue
        else:
            logger.info("[!] Performing '%s' actions on region: '%s'", args.sanitize_option, current_region)
            logger.info("========================================================================================\n")
            if args.sanitize_option == 'delete':
                Update.update_ssm_preferences(boto_client=ssm_client, region=current_region)
                del_resource = Delete(obj)
                if del_resource.run_delete():
                    logger.info("[+] **All VPC delete actions successfully performed in '%s' region**", current_region)
            elif args.sanitize_option == "modify":
                Update.update_ssm_preferences(boto_client=ssm_client, region=current_region)
                update_resource = Update(obj)
                if update_resource.run_update():
                    logger.info("[+] **All VPC update actions successfully performed in '%s' region**\n\n", current_region)


if __name__ == "__main__":
    main()
