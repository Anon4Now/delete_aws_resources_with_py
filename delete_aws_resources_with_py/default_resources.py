"""Module containing classes that are used to find and delete resources"""

# Standard Library imports
from dataclasses import dataclass

# Local app imports
from delete_aws_resources_with_py import (
    create_boto3_client,
    create_boto3_resource,
    create_logger,
    error_handler
)

logger = create_logger()


@dataclass
class Resources:
    resource: str = None
    region: str = None
    current_vpc_resource = None

    def __post_init__(self):
        self.vpc_id = self.get_vpcs(self.region)
        self.boto_resource = create_boto3_resource(self.resource, region=self.region)
        self.boto_client = create_boto3_client(self.resource, region=self.region)
        self.current_vpc_resource = self.boto_resource.Vpc(self.vpc_id)
        self.igw = self.current_vpc_resource.internet_gateways.all()
        subnets = self.current_vpc_resource.subnets.all()
        self.default_subnets = [self.boto_resource.Subnet(subnet.id) for subnet in subnets if subnet.default_for_az]
        self.route_tables = self.current_vpc_resource.route_tables.all()
        self.acls = self.current_vpc_resource.network_acls.all()
        self.sgs = self.current_vpc_resource.security_groups.all()

    @error_handler
    def get_vpcs(self, current_region: str) -> str:
        vpcs = create_boto3_client(self.resource, region=current_region).describe_vpcs(
            Filters=[
                {
                    'Name': 'isDefault',
                    'Values': [
                        'true',

                    ],
                },
            ]
        )

        # add vpc's to instance attribute
        for vpc in vpcs['Vpcs']:
            return vpc['VpcId']



# @dataclass
# class AlterResources:
#     resource: str
#     skip_region_list: list
#     args: str
#
#     def __post_init__(self):
#         self.region_list = []
#         get_region_object = create_boto3_client(self.resource).describe_regions()
#         for region in get_region_object['Regions']:
#             if region['RegionName'] in self.skip_region_list:
#                 self.region_list.append(region['RegionName'])
#
#     def delete_resources(self, obj):
#
#         for igw in obj.igw:
#             logger.info("[!] Attempting to detach and delete IGW-ID: '%s'", igw.id)
#             igw.detach_from_vpc(VpcId=obj.vpc_id)
#             igw.delete()
#             logger.info("[+] '%s' was successfully detached and deleted", igw.id)
#         # TODO: NEED TO CONTINUE TO CHECK THE OUTPUT OF THE ABOVE VAR
#         # TODO: TRYING TO CONSOLIDATE ALL DELETE CALLS TO ONE METHOD AND UPDATE TO ANOTHER METHOD
#
#     # @error_handler
#     # def get_regions(self, service: str, skip_region_list: list) -> list:
#     #     """
#     #     Will generate a list of regions to take action on
#     #     :return: List containing the regions to delete resources from
#     #     :raise: AWS API "Boto3" ClientErrors
#     #     """
#     #     region_list = []
#     #     print(skip_region_list)
#     #
#     #     get_region_object = create_boto3_client(service).describe_regions()
#     #     for region in get_region_object['Regions']:
#     #         if region['RegionName'] in skip_region_list:
#     #             region_list.append(region['RegionName'])
#     #     return region_list
#
#     # def deleteIGW(self):
#     #     print(self.current_vpc_resource)
#
#     #     internetGateways = vpcResource.internet_gateways.all()
#     #
#     #     # attempt to delete the resource(s)
#     #     if internetGateways:
#     #         for igw in internetGateways:
#     #             print(f'[*] Attempting to detach & remove IGW-ID: {igw.id}...')
#     #             igw.detach_from_vpc(
#     #                 VpcId=self.vpc_id
#     #             )
#     #             # Use the DryRun if test without deletion is needed
#     #             igw.delete(
#     #                 # DryRun=True
#     #             )
#     #             logger.info(f'[+] {igw.id} was successfully detached & removed\n')
#     #
#     # def deleteSubnet(self):
#     #     vpcResource = self.ec2.Vpc(self.vpcid)
#     #     subnets = vpcResource.subnets.all()
#     #     defaultSubnets = [self.ec2.Subnet(subnet.id) for subnet in subnets if subnet.default_for_az]
#     #
#     #     # attempt to delete the resource(s)
#     #     if defaultSubnets:
#     #         for subnet in defaultSubnets:
#     #             print(f'[*] Attempting to remove Subnet: {subnet.id}')
#     #             # Use the DryRun if test without deletion is needed
#     #             subnet.delete(
#     #                 # DryRun=True
#     #             )
#     #             logger.info(f'[+] {subnet.id} was successfully removed\n')
#     #
#     # def deleteRouteTable(self):
#     #     vpcResource = self.ec2.Vpc(self.vpcid)
#     #     routeTables = vpcResource.route_tables.all()
#     #
#     #     # attempt to delete the resource(s)
#     #     if routeTables:
#     #         for routeTable in routeTables:
#     #             #  found the route table associations
#     #             associatedAttribute = [routeTable.associations_attribute for routeTable in routeTables]
#     #             #  check to see if it is the default the route table, this cannot be removed
#     #             if [rtb_ass[0]['RouteTableId'] for rtb_ass in associatedAttribute if rtb_ass[0]['Main'] is True]:
#     #                 print(f'[!] {routeTable.id} is the main route table, continue...\n')
#     #                 continue
#     #             print(f'[*] Attempting to remove Route Table: {routeTable.id}')
#     #             table = self.ec2.RouteTable(routeTable.id)
#     #             # Use the DryRun if test without deletion is needed
#     #             table.delete(
#     #                 # DryRun=True
#     #             )
#     #             logger.info(f'[+] {routeTable.id} was successfully removed\n')
#     #
#     # def deleteAcl(self, option):
#     #     vpcResource = self.ec2.Vpc(self.vpcid)
#     #     acls = vpcResource.network_acls.all()
#     #
#     #     # attempt to delete the resource(s)
#     #     if acls:
#     #         for acl in acls:
#     #             #  check to see if the NACL is default, this cannot be removed
#     #             if acl.is_default:
#     #                 if not option == "deleteOnlyOption":
#     #                     print(f'[!] {acl.id} is the default NACL, attempting to remove default rules \n')
#     #                     if self.updateResource.updateInboundNaclRule(acl.id):
#     #                         print(f'[+] Ingress NACL Rule was removed for {acl.id}')
#     #                     else:
#     #                         print(f'[+] Failed to remove Ingress NACL Rule for {acl.id}')
#     #                     if self.updateResource.updateOutboundNaclRule(acl.id):
#     #                         print(f'[+] Egress NACL rule was remove for {acl.id}')
#     #                     else:
#     #                         print(f'[-] Failed to remove Egress rule for {acl.id}')
#     #                     print(f'[!] Continuing Script \n')
#     #                     continue
#     #                 else:
#     #                     print(f'[!] {acl.id} is the default NACL, taking no action and continuing \n')
#     #                     continue
#     #             else:
#     #                 if not option == "modifyOnlyOption":
#     #                     print(f'[!] Attempting to remove ACL-ID {acl.id}')
#     #                     acl.delete()
#     #                     logger.info("[+] Successfully removed acl '%s'", acl.id)
#     #
#     # def deleteSecurityGroup(self, option):
#     #     vpcResource = self.ec2.Vpc(self.vpcid)
#     #     securityGroups = vpcResource.security_groups.all()
#     #
#     #     # attempt to delete the resource(s)
#     #     if securityGroups:
#     #         for sg in securityGroups:
#     #             #  check to see if the NACL is default, this cannot be removed
#     #             if sg.group_name == 'default':
#     #                 if not option == "deleteOnlyOption":
#     #                     print(f'[!] {sg} is the default SG, attempting to remove default rules \n')
#     #                     if self.updateResource.removeInboundSecurityGroupRule(sg.id):
#     #                         print(f'[+] Ingress SG Rule was removed for {sg.id}')
#     #                     else:
#     #                         print(f'[+] Failed to remove Ingress SG Rule for {sg.id}')
#     #                     if self.updateResource.removeOutboundSecurityGroupRule(sg.id):
#     #                         print(f'[+] Egress SG rule was remove for {sg.id}')
#     #                     else:
#     #                         print(f'[-] Failed to remove Egress rule for {sg.id}')
#     #                     print(f'[!] Continuing Script \n')
#     #                     continue
#     #                 else:
#     #                     print(f'[!] {sg.id} is the default SG, taking no action and continuing \n')
#     #                     continue
#     #             else:
#     #                 if not option == "modifyOnlyOption":
#     #                     print(f'[!] Attempting to remove SG-ID {sg.id}')
#     #                     sg.delete()
#     #                     logger.info("[+] Successfully removed SG '%s'", sg.id)
#     #
#     # def deleteVPC(self):
#     #     vpcResource = self.ec2.Vpc(self.vpcid)
#     #
#     #     # attempt to delete the resource(s)
#     #     print(f'[*] Attempting to remove VPC-ID: {vpcResource.id}')
#     #     # Use the DryRun if test without deletion is needed
#     #     vpcResource.delete(
#     #         # DryRun=True
#     #     )
#     #     logger.info(f'[+] {vpcResource.id} was successfully removed\n')
#
#     def call_methods(self):
#         """
#         Checks the args passed by user and call appropriate methods
#         :return: Boolean for success=True or failure=False
#         """
#         for current_region in self.region_list:
#             obj = Resources(resource=self.resource, region=current_region)
#             if self.args == 'all':
#                 logger.info("[!] Performing '%s' actions on region: '%s'", self.args, current_region)
#                 self.delete_resources(obj)
#                 # self.deleteSubnet()
#                 # self.deleteRouteTable()
#                 # self.deleteAcl(self.args)
#                 # self.deleteSecurityGroup(self.args)
#                 # self.deleteVPC()
#                 # TODO: ADD THE SSM PARAMETER ACTION
