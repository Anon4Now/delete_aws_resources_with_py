"""Module containing the main script to run"""
from typing import Any, List, Tuple

# !/usr/bin/env python

# Local app imports
from delete_aws_resources_with_py.utils import (
    logger,
    create_boto3,
    get_args,
    SKIP_REGION_LIST,
)
from delete_aws_resources_with_py.resource_updates import (
    UpdateNaclResource,
    UpdateSgResource
)
from delete_aws_resources_with_py.resource_delete import Delete
from delete_aws_resources_with_py.default_resources import Resource
from delete_aws_resources_with_py.errors import NoDefaultVpcExistsError, UserArgNotFoundError
from delete_aws_resources_with_py.change_ssm_preferences import SsmPreference


#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'


def execute_changes_on_resources(resource_obj: Resource, user_arg: str) -> bool:
    if not resource_obj.vpc_id:
        raise NoDefaultVpcExistsError
    if user_arg == 'delete':
        del_resource = Delete(resource_obj)
        if del_resource.delete_resources():
            return True
    elif user_arg == "modify":
        update_sg_resource = UpdateSgResource(resource_obj)
        update_nacl_resource = UpdateNaclResource(resource_obj)
        if update_sg_resource.revoke_sg_rules() and update_nacl_resource.update_nacl_rules():
            return True


def check_user_arg_response(user_arg: str) -> bool:
    """Check to see if arg passed is valid"""
    if user_arg not in ['delete', 'modify']:  # validate cmd line arg
        raise UserArgNotFoundError
    return True


def get_region_list() -> List[str]:
    """Return a list of regions to be iterated through"""
    get_region_object = create_boto3(service='ec2', boto_type='boto_client').describe_regions()
    return [x['RegionName'] for x in get_region_object['Regions'] if x['RegionName'] in SKIP_REGION_LIST]


def create_boto_objects(current_region: str) -> Tuple[Any, Any, Any]:
    ssm_client = create_boto3(service='ssm', boto_type='boto_client', region=current_region)
    boto_resource = create_boto3(service='ec2', boto_type="boto_resource", region=current_region)
    boto_client = create_boto3(service='ec2', boto_type="boto_client", region=current_region)
    return ssm_client, boto_client, boto_resource


def main() -> bool:
    args = get_args()
    if not check_user_arg_response(args):
        raise UserArgNotFoundError
    region_list = get_region_list()
    for current_region in region_list:
        try:
            boto_tup = create_boto_objects(current_region)
            obj = Resource(boto_resource=boto_tup[2], boto_client=boto_tup[1],
                           region=current_region)  # instantiate the Resource object
            logger.info("[!] Performing '%s' actions on region: '%s'", args, current_region)
            logger.info("========================================================================================\n")
            SsmPreference(ssm_client=boto_tup[0], region=current_region).check_ssm_preferences()
            if execute_changes_on_resources(obj, args):
                logger.info("[+] **All VPC %s actions successfully performed in '%s' region**", args,
                            current_region)
                return True
        except NoDefaultVpcExistsError:
            logger.info("[!] Region: '%s' does not have a default VPC, continuing\n", current_region)
            continue


if __name__ == "__main__":
    try:
        main()
    except UserArgNotFoundError:
        logger.error("[-] Entered an incorrect option, use -h or --help for more information")
