"""Module containing the main script to run"""

# !/usr/bin/env python

# Local app imports
from delete_aws_resources_with_py import (
    create_logger,
    create_boto3_client,
    getArgs,
    Resources

)

#  VPC resources created by AWS 'https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html'

logger = create_logger()
SKIP_REGIONS = ["us-east-1", "us-west-2"]


def delete_resources(obj):
    for igw in obj.igw:
        logger.info("[!] Attempting to detach and delete IGW-ID: '%s' in Region: '%s'", igw.id, obj.region)
        igw.detach_from_vpc(VpcId=obj.vpc_id)
        igw.delete()
        logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted", igw.id, obj.region)
    for subnet in obj.default_subnets:
        logger.info("[!] Attempting to detach and delete Subnet-ID: '%s' in Region: '%s'", subnet.id, obj.region)
        subnet.delete()
        logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted", subnet.id, obj.region)
    for routeTable in obj.route_tables:
        #  found the route table associations
        associatedAttribute = [routeTable.associations_attribute for routeTable in obj.route_tables]
        #  check to see if it is the default the route table, this cannot be removed
        if [rtb_ass[0]['RouteTableId'] for rtb_ass in associatedAttribute if rtb_ass[0]['Main'] is True]:
            logger.info("[!] '%s'' is the main route table, cannot delete continuing...\n", routeTable.id)
            continue
        logger.info("[!] Attempting to detach and delete Subnet-ID: '%s' in Region: '%s'", routeTable.id, obj.region)
        obj.boto_resource.RouteTable(routeTable.id).delete()
        logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted", routeTable.id, obj.region)

        # TODO: NEED TO ADD NACL DELETE
        # TODO: NEED TO ADD SG DELETE
        # TODO: NEED TO ADD VPC DELETE


def update_resources():
    pass
    # TODO: NEED TO ADD UPDATE CONTENT


def main():
    args = getArgs()
    get_region_object = create_boto3_client('ec2').describe_regions()
    region_list = [x['RegionName'] for x in get_region_object['Regions'] if x['RegionName'] in SKIP_REGIONS]
    for current_region in region_list:
        obj = Resources(resource='ec2', region=current_region)
        if args.sanitize_option == 'all':
            logger.info("[!] Performing '%s' actions on region: '%s' \n", args.sanitize_option, current_region)
            delete_resources(obj)


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
