"""Module containing the main script to run"""
from typing import Any

# !/usr/bin/env python

# Local app imports
from delete_aws_resources_with_py.utils import (
    logger,
    create_boto3,
    getArgs,
    SKIP_REGION_LIST,
)
from delete_aws_resources_with_py.resource_updates import (
    UpdateNaclResource,
    UpdateSgResource,
    update_ssm_preferences
)
from delete_aws_resources_with_py.resource_delete import Delete
from delete_aws_resources_with_py.default_resources import Resource
from delete_aws_resources_with_py.errors import NoDefaultVpcExistsError, UserArgNotFoundError


#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'


def execute_changes_on_resources(user_arg: str, resource_obj: Resource, ssm_client: Any, current_region: str) -> bool:
    if user_arg not in ['delete', 'modify']:  # validate cmd line arg
        raise UserArgNotFoundError
    elif not resource_obj.vpc_id:
        raise NoDefaultVpcExistsError
    else:
        logger.info("[!] Performing '%s' actions on region: '%s'", user_arg, current_region)
        logger.info("========================================================================================\n")
        update_ssm_preferences(boto_client=ssm_client, region=current_region)
        if user_arg == 'delete':
            del_resource = Delete(resource_obj)
            if del_resource.delete_resources():
                logger.info("[+] **All VPC delete actions successfully performed in '%s' region**", current_region)
                return True
        elif user_arg == "modify":
            update_sg_resource = UpdateSgResource(resource_obj)
            update_nacl_resource = UpdateNaclResource(resource_obj)
            if update_sg_resource.revoke_sg_rules() and update_nacl_resource.update_nacl_rules():
                logger.info("[+] **All VPC update actions successfully performed in '%s' region**\n\n", current_region)
                return True


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
        try:
            execute_changes_on_resources(args.sanitize_option, obj, ssm_client, current_region)
        except UserArgNotFoundError:
            logger.error("[-] Entered an incorrect option, use -h or --help for more information")
            break
        except NoDefaultVpcExistsError:
            logger.info("[!] Region: '%s' does not have a default VPC, continuing", current_region)
            continue
        # if args.sanitize_option not in ['delete', 'modify']:  # validate cmd line arg
        #     logger.error("[-] Entered an incorrect option, use -h or --help for more information")
        #     break
        # elif not obj.vpc_id:
        #     logger.info("[!] Region: '%s' does not have a default VPC, continuing", current_region)
        #     continue
        # else:
        #     logger.info("[!] Performing '%s' actions on region: '%s'", args.sanitize_option, current_region)
        #     logger.info("========================================================================================\n")
        #     if args.sanitize_option == 'delete':
        #         Update.update_ssm_preferences(boto_client=ssm_client, region=current_region)
        #         del_resource = Delete(obj)
        #         if del_resource.run_delete():
        #             logger.info("[+] **All VPC delete actions successfully performed in '%s' region**", current_region)
        #     elif args.sanitize_option == "modify":
        #         Update.update_ssm_preferences(boto_client=ssm_client, region=current_region)
        #         update_resource = Update(obj)
        #         if update_resource.run_update():
        #             logger.info("[+] **All VPC update actions successfully performed in '%s' region**\n\n", current_region)


if __name__ == "__main__":
    main()
