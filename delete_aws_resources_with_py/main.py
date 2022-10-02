"""Module containing the main script to run"""

# !/usr/bin/env python

# Third-party imports
from botocore.exceptions import ClientError

# Local app imports
from delete_aws_resources_with_py import (
    logger,
    create_boto3,
    error_handler,
    getArgs,
    Resource
)
from delete_aws_resources_with_py.resource_updates import (
    Delete,
    Update
)

#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'

# TODO: MOVE THIS TO A CONFIG.JSON FILE
SKIP_REGIONS = ["us-east-1", "us-west-2"]  # Update this list for whatever region you **DO NOT WANT TO BE EFFECTED**


# def delete_resources(obj: Resource) -> None:
#     """
#     Function that takes in an instantiated Resources object and uses attrs on object
#     to perform detach/delete actions related to default VPCs.
#     Attempts to take actions on the following resources:
#     - Internet Gateway
#     - Subnets
#     - Route Tables
#     - Network Access Control Lists
#     - Security Groups
#     :param obj: (required) Instantiated Resource Class object passed from main()
#     :return: None
#     """
#     """Actions related to Internet Gateway deletion from default VPC"""
#     for igw in obj.igw:
#         logger.info("[!] Attempting to detach and delete IGW-ID: '%s' in Region: '%s'", igw.id, obj.region)
#         igw.detach_from_vpc(VpcId=obj.vpc_id)
#         igw.delete()
#         logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", igw.id, obj.region)
#
#     """Actions related to Subnet deletion from default VPC"""
#     for subnet in obj.default_subnets:
#         logger.info("[!] Attempting to detach and delete Subnet-ID: '%s' in Region: '%s'", subnet.id, obj.region)
#         subnet.delete()
#         logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", subnet.id, obj.region)
#
#     """Actions related to RouteTable deletion from default VPC; cannot delete the default RouteTable"""
#     for route_table in obj.route_tables:
#         #  found the route table associations
#         associated_attribute = [routeTable.associations_attribute for routeTable in obj.route_tables]
#         #  check to see if it is the default the route table, this cannot be removed
#         if [rtb_ass[0]['RouteTableId'] for rtb_ass in associated_attribute if rtb_ass[0]['Main'] is True]:
#             logger.info("[!] '%s'' is the main route table, this cannot be removed continuing\n", route_table.id)
#             continue
#         logger.info("[!] Attempting to detach and delete Subnet-ID: '%s' in Region: '%s'", route_table.id, obj.region)
#         obj.boto_resource.RouteTable(route_table.id).delete()
#         logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", route_table.id, obj.region)
#
#     """Actions related to NACL deletion from default VPC; cannot delete the default NACL"""
#     for acl in obj.acls:
#         if acl.is_default:
#             logger.info("[!] '%s' is the default NACL, this cannot be removed continuing\n", acl.id)
#             continue
#         else:
#             logger.info("[!] Attempting to remove NACL-ID: '%s' for Region: '%s'", acl.id, obj.region)
#             acl.delete()
#             logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", acl.id, obj.region)
#
#     """Actions related to SG deletion from default VPC; cannot delete the default SG"""
#     for sg in obj.sgs:
#         if sg.group_name == 'default':
#             logger.info("[!] '%s' is the default SG, this cannot be removed continuing\n", sg.id)
#             continue
#         else:
#             logger.info("[!] Attempting to remove SG-ID: '%s' for Region: '%s'", sg.id, obj.region)
#             sg.delete()
#             logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", sg.id, obj.region)
#
#     """Actions related to the deletion of the default VPC"""
#     logger.info("[!] Attempting to remove VPC-ID: '%s' for Region: '%s'", obj.vpc_id, obj.region)
#     obj.current_vpc_resource.delete()
#     logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n\n", obj.vpc_id, obj.region)


# def update_resources(obj: Resource) -> None:
#     """
#     Function that takes in an instantiated Resources object and uses attrs on object
#     to perform modification actions related to default VPCs.
#     Attempts to take actions on the following resources:
#     - Network Access Control Lists
#     - Security Groups
#     :param obj: (required) Instantiated Resource Class object passed from main()
#     :return: None
#     """
#     """Actions related to removing inbound/outbound rules from the default NACL"""
#     for acl in obj.acls:
#         if acl.is_default:
#             logger.info("[!] Attempting to remove inbound & outbound NACL rule for '%s'", acl.id)
#             egress_flags = [True, False]
#             [obj.boto_client.delete_network_acl_entry(Egress=x, NetworkAclId=acl.id, RuleNumber=100) for x in
#              egress_flags]  # use list comp to pass in the True/False bool into the AWS API call; both are needed
#             logger.info("[!] Successfully removed inbound & outbound NACL rules for '%s'\n", acl.id)
#
#     """Actions related to removing inbound/outbound rules from the default SG"""
#     for sg in obj.sgs:
#         if sg.group_name == 'default':
#             sg_rule = obj.boto_client.describe_security_group_rules(
#                 Filters=[
#                     {
#                         'Name': 'group-id',
#                         'Values': [
#                             sg.id
#                         ]
#                     }
#                 ]
#             )
#             for el in sg_rule['SecurityGroupRules']:
#                 if el['IsEgress']:
#                     logger.info("[!] Attempting to remove outbound SG rule '%s' in Region: '%s'",
#                                 el['SecurityGroupRuleId'], obj.region)
#                     obj.boto_client.revoke_security_group_egress(GroupId=sg.id,
#                                                                  SecurityGroupRuleIds=[el['SecurityGroupRuleId']])
#                     logger.info("[+] Outbound SG rule '%s' in Region: '%s' was successfully removed\n",
#                                 el['SecurityGroupRuleId'], obj.region)
#                 else:
#                     logger.info("[!] Attempting to remove inbound SG rule '%s' in Region: '%s'",
#                                 el['SecurityGroupRuleId'], obj.region)
#                     obj.boto_client.revoke_security_group_ingress(GroupId=sg.id,
#                                                                   SecurityGroupRuleIds=[el['SecurityGroupRuleId']])
#                     logger.info("[+] Inbound SG rule '%s' in Region: '%s' was successfully removed\n",
#                                 el['SecurityGroupRuleId'], obj.region)
#
#
# def update_ssm_preferences(boto_client, region) -> None:
#     """
#     Function designed to check the SSM document preferences in each region.
#     If they are open to the public, update the preference to be private to the account.
#     :param boto_client: (required) Instantiated boto3 client for the current region in the loop
#     :param region: (required) Current region in the loop passed from main()
#     :return: Boolean depicting the success of the actions (True = success/False = failure)
#     """
#     public_share_setting = "/ssm/documents/console/public-sharing-permission"  # path provided by BOTO3 API docs
#     get_current_acct_settings = boto_client.get_service_setting(SettingId=public_share_setting)  # check current setting
#     current_setting = get_current_acct_settings['ServiceSetting']['SettingValue']
#     if current_setting == 'Enable':
#         logger.info(
#             "[!] SSM Document preferences allows public access with status '%s' in Region: '%s', attempting to update",
#             current_setting, region)
#         boto_client.update_service_setting(SettingId=public_share_setting, SettingValue="Disable")  # update setting
#         logger.info("[+] Preferences successfully updated to 'Disable' in Region: '%s'\n", region)
#     else:
#         logger.info("[+] SSM Document preferences already block public access with status '%s', no action taken\n",
#                     current_setting)


@error_handler
def main():
    args = getArgs()
    get_region_object = create_boto3(service='ec2', boto_type='boto_client').describe_regions()
    region_list = [x['RegionName'] for x in get_region_object['Regions'] if
                   x['RegionName'] in SKIP_REGIONS]
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
                    logger.info("[+] **All VPC update actions successfully performed in '%s' region**", current_region)


if __name__ == "__main__":
    main()
