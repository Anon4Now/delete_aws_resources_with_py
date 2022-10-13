"""Module containing the main script to run"""

# !/usr/bin/env python

# Standard Library imports
from typing import List, NamedTuple
from collections import namedtuple


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
    """
    Function that instantiates the classes from the resource_* modules.

    Uses the methods to either delete the resources or update them based on user arg.

    :param resource_obj: (required) An instantiated resource object from default_resources module
    :param user_arg: (required) A string representing the arg passed by user (i.e., 'delete' or 'modify')
    :return: A boolean representing whether the requested action was completed successfully

    :raise A custom error class that will be used to log that no default VPC exists in the current region
    """
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
    """
    Check to see if arg passed from user is valid.

    Needs to be either 'delete' or 'modify', will raise error is neither.

    :param user_arg: (required) A string representing the arg passed at the CLI
    :return A boolean representing whether the arg is one of the two correct options

    :raise A custom error that will log out that the arg passed was incorrect
    """
    if user_arg not in ['delete', 'modify']:  # validate cmd line arg
        raise UserArgNotFoundError
    return True


def get_region_list() -> List[str]:
    """
    Return a list of active regions to be iterated through.

    :return A list containing all active regions NOT listed in the SKIP_REGION_LIST (config.json)
    """
    get_region_object = create_boto3(service='ec2', boto_type='boto_client').describe_regions()
    return [x['RegionName'] for x in get_region_object['Regions'] if x['RegionName'] in SKIP_REGION_LIST]


def create_boto_objects(current_region: str):
    """
    Basic function that will generate three instantiated boto objects.

    These will be returned as a NamedTuple.

    :param current_region: (required) A string containing the current region, used to instantiate the objects
    :return: A NamedTuple containing the instantiated boto objects
    """
    boto_tuple = namedtuple('boto_tuple', ['ssm_client', 'ec2_resource', 'ec2_client'])
    return boto_tuple(
        ssm_client=create_boto3(service='ssm', boto_type='boto_client', region=current_region),
        ec2_resource=create_boto3(service='ec2', boto_type="boto_resource", region=current_region),
        ec2_client=create_boto3(service='ec2', boto_type="boto_client", region=current_region)
    )


def main() -> None:
    """
    Main function that will call the other functions in the main module.

    This will log out the details on the actions being attempted and whether
    all actions performed successfully.

    :raise A custom error (UserArgNotFoundError) that represents when the user enters an incorrect arg

    :raise A custom error (NoDefaultVpcExistsError) that represents when a region doesn't have a default VPC
    """
    args = get_args()
    if not check_user_arg_response(args):
        raise UserArgNotFoundError
    region_list = get_region_list()
    for current_region in region_list:
        try:
            boto_tup = create_boto_objects(current_region)
            obj = Resource(boto_resource=boto_tup.ec2_resource, boto_client=boto_tup.ec2_client,
                           region=current_region)  # instantiate the Resource object
            logger.info("[!] Performing '%s' actions on region: '%s'", args, current_region)
            logger.info("========================================================================================\n")
            SsmPreference(ssm_client=boto_tup.ssm_client, region=current_region).check_ssm_preferences()
            if execute_changes_on_resources(obj, args):
                logger.info("[+] **All VPC %s actions successfully performed in '%s' region**\n\n", args,
                            current_region)
        except NoDefaultVpcExistsError:
            logger.info("[!] Region: '%s' does not have a default VPC, continuing\n", current_region)
            continue


if __name__ == "__main__":
    try:
        main()
    except UserArgNotFoundError:
        logger.error("[-] Entered an incorrect option, use -h or --help for more information")
