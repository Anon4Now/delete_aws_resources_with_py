"""Module that contains classes for updating resources"""

# Third-party imports
from botocore.exceptions import ClientError

# Local App imports
from delete_aws_resources_with_py.default_resources import Resource
from delete_aws_resources_with_py.utils import logger


class Delete:
    """Action-oriented class for deleting default resources"""

    def __init__(self, resource_obj: Resource) -> None:
        """
        Initializer that takes an instantiated Resource class object with VPC data.

        :param resource_obj: (required) Instantiated Resource object with necessary data
        """
        self.resource_obj = resource_obj

    def delete_default_igw(self) -> bool:
        """Actions related to Internet Gateway deletion from default VPC"""
        try:
            for igw in self.resource_obj.igw:
                logger.info("[!] Attempting to detach and delete IGW-ID: '%s' in Region: '%s'", igw.id,
                            self.resource_obj.region)
                igw.detach_from_vpc(VpcId=self.resource_obj.vpc_id)
                igw.delete()
                logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", igw.id,
                            self.resource_obj.region)
        except ClientError:
            raise
        else:
            return True

    def delete_default_subnet(self) -> bool:
        """Actions related to Subnet deletion from default VPC"""
        try:
            for subnet in self.resource_obj.subnet:
                logger.info("[!] Attempting to detach and delete Subnet-ID: '%s' in Region: '%s'", subnet.id,
                            self.resource_obj.region)
                subnet.delete()
                logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", subnet.id,
                            self.resource_obj.region)
        except ClientError:
            raise
        else:
            return True

    def delete_default_rtb(self) -> bool:
        """Actions related to RouteTable deletion from default VPC; cannot delete the default RouteTable"""
        try:
            for route_table in self.resource_obj.route_table:
                #  found the route table associations
                associated_attribute = [routeTable.associations_attribute for routeTable in
                                        self.resource_obj.route_table]
                #  check to see if it is the default the route table, this cannot be removed
                if [rtb_ass[0]['RouteTableId'] for rtb_ass in associated_attribute if rtb_ass[0]['Main'] is True]:
                    logger.info("[!] '%s'' is the main route table, this cannot be removed continuing\n",
                                route_table.id)
                    continue
                logger.info("[!] Attempting to detach and delete Subnet-ID: '%s' in Region: '%s'", route_table.id,
                            self.resource_obj.region)
                self.resource_obj.boto_resource.RouteTable(route_table.id).delete()
                logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", route_table.id,
                            self.resource_obj.region)
        except ClientError:
            raise
        else:
            return True

    def delete_default_nacl(self) -> bool:
        """Actions related to NACL deletion from default VPC; cannot delete the default NACL"""
        try:
            for acl in self.resource_obj.acl:
                if acl.is_default:
                    logger.info("[!] '%s' is the default NACL, this cannot be removed continuing\n", acl.id)
                    continue
                else:
                    logger.info("[!] Attempting to remove NACL-ID: '%s' for Region: '%s'", acl.id,
                                self.resource_obj.region)
                    acl.delete()
                    logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", acl.id,
                                self.resource_obj.region)
        except ClientError:
            raise
        else:
            return True

    def delete_default_sg(self) -> bool:
        """Actions related to SG deletion from default VPC; cannot delete the default SG"""
        try:
            for sg in self.resource_obj.sgs:
                if sg.group_name == 'default':
                    logger.info("[!] '%s' is the default SG, this cannot be removed continuing\n", sg.id)
                    continue
                else:
                    logger.info("[!] Attempting to remove SG-ID: '%s' for Region: '%s'", sg.id,
                                self.resource_obj.region)
                    sg.delete()
                    logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", sg.id,
                                self.resource_obj.region)
        except ClientError:
            raise
        else:
            return True

    def delete_default_vpc(self) -> bool:
        """Actions related to the deletion of the default VPC"""
        try:
            logger.info("[!] Attempting to remove VPC-ID: '%s' for Region: '%s'", self.resource_obj.vpc_id,
                        self.resource_obj.region)
            self.resource_obj.current_vpc_resource.delete()
            logger.info("[+] Default VPC in Region: '%s' was successfully detached and deleted\n\n", self.resource_obj.vpc_id,
                        self.resource_obj.region)
        except ClientError:
            raise
        else:
            return True

    def run_delete(self) -> bool:
        """Method to run all the action methods and return True if all successful"""
        try:
            if self.delete_default_igw() and \
                    self.delete_default_subnet() and \
                    self.delete_default_rtb() and \
                    self.delete_default_nacl() and \
                    self.delete_default_sg() and \
                    self.delete_default_vpc():
                return True
        except ClientError:
            raise


class Update:
    """Action-oriented class for updating default resources"""

    def __init__(self, resource_obj: Resource) -> None:
        """
        Initializer that takes an instantiated Resource class object with VPC data.

        :param resource_obj: (required) Instantiated Resource object with necessary data
        """
        self.resource_obj = resource_obj

    def update_nacl_rules(self) -> bool:
        """Actions related to removing inbound/outbound rules from the default NACL"""
        try:
            for acl in self.resource_obj.acl:
                if acl.is_default:
                    logger.info("[!] Attempting to remove inbound & outbound NACL rule for '%s'", acl.id)
                    egress_flags = [True, False]
                    [self.resource_obj.boto_client.delete_network_acl_entry(Egress=x, NetworkAclId=acl.id,
                                                                            RuleNumber=100)
                     for x in
                     egress_flags]  # use list comp to pass in the True/False bool into the AWS API call; both are needed
                    logger.info("[!] Successfully removed inbound & outbound NACL rules for '%s'\n", acl.id)
        except ClientError:
            raise
        else:
            return True

    def update_sg_rules(self) -> bool:
        """Actions related to removing inbound/outbound rules from the default SG"""
        try:
            for sg in self.resource_obj.sgs:
                if sg.group_name == 'default':
                    sg_rule = self.resource_obj.boto_client.describe_security_group_rules(
                        Filters=[
                            {
                                'Name': 'group-id',
                                'Values': [
                                    sg.id
                                ]
                            }
                        ]
                    )
                    for el in sg_rule['SecurityGroupRules']:
                        if el['IsEgress']:
                            logger.info("[!] Attempting to remove outbound SG rule '%s' in Region: '%s'",
                                        el['SecurityGroupRuleId'], self.resource_obj.region)
                            self.resource_obj.boto_client.revoke_security_group_egress(GroupId=sg.id,
                                                                                       SecurityGroupRuleIds=[
                                                                                           el['SecurityGroupRuleId']])
                            logger.info("[+] Outbound SG rule '%s' in Region: '%s' was successfully removed\n",
                                        el['SecurityGroupRuleId'], self.resource_obj.region)
                        else:
                            logger.info("[!] Attempting to remove inbound SG rule '%s' in Region: '%s'",
                                        el['SecurityGroupRuleId'], self.resource_obj.region)
                            self.resource_obj.boto_client.revoke_security_group_ingress(GroupId=sg.id,
                                                                                        SecurityGroupRuleIds=[
                                                                                            el['SecurityGroupRuleId']])
                            logger.info("[+] Inbound SG rule '%s' in Region: '%s' was successfully removed\n",
                                        el['SecurityGroupRuleId'], self.resource_obj.region)
        except ClientError:
            raise
        else:
            return True

    def run_update(self) -> bool:
        """Method to execute other action methods on class and return True if all successful"""
        try:
            if self.update_nacl_rules() and self.update_sg_rules():
                return True
        except ClientError:
            raise

    @staticmethod
    def update_ssm_preferences(boto_client, region) -> None:
        """
        Function designed to check the SSM document preferences in each region.
        If they are open to the public, update the preference to be private to the account.
        :param boto_client: (required) Instantiated boto3 client for the current region in the loop
        :param region: (required) Current region in the loop passed from main()
        :return: Boolean depicting the success of the actions (True = success/False = failure)
        """
        public_share_setting = "/ssm/documents/console/public-sharing-permission"  # path provided by BOTO3 API docs
        get_current_acct_settings = boto_client.get_service_setting(
            SettingId=public_share_setting)  # check current setting
        current_setting = get_current_acct_settings['ServiceSetting']['SettingValue']
        if current_setting == 'Enable':
            logger.info(
                "[!] SSM Document preferences allows public access with status '%s' in Region: '%s', attempting to update",
                current_setting, region)
            boto_client.update_service_setting(SettingId=public_share_setting, SettingValue="Disable")  # update setting
            logger.info("[+] Preferences successfully updated to 'Disable' in Region: '%s'\n", region)
        else:
            logger.info("[+] SSM Document preferences already block public access with status '%s', no action taken\n",
                        current_setting)
