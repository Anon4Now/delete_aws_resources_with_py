"""Module that contains classes for updating resources"""
from typing import Union, Any, List, Dict
from abc import ABC, abstractmethod

# Third-party imports
from botocore.exceptions import ClientError

# Local App imports
from delete_aws_resources_with_py.default_resources import Resource
from delete_aws_resources_with_py.utils import logger


class UpdateResource(ABC):
    @abstractmethod
    def __init__(self, resource_obj: Resource):
        self.resource_obj = resource_obj


class UpdateNaclResource(UpdateResource):
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


class UpdateSgResource(UpdateResource):

    def __init__(self, resource_obj: Resource) -> None:
        """
        Initializer that takes an instantiated Resource class object with VPC data.

        :param resource_obj: (required) Instantiated Resource object with necessary data
        """
        self.resource_obj = resource_obj

    @staticmethod
    def find_egress_sg_rule(sg_rules: Dict[str, list]):
        # return {key: val['SecurityGroupRules'] for key, val in sg_rules.items()}
        out_dict = {}
        for k, v in sg_rules.items():
            for el in v:
                if el['IsEgress']:
                    out_dict[k] = el['SecurityGroupRuleId']
        return out_dict
        # logger.info("[!] Attempting to remove outbound SG rule '%s' in Region: '%s'",
        #             el['SecurityGroupRuleId'], self.resource_obj.region)
        # self.revoke_egress_sg_rule(sg.id, el['SecurityGroupRuleId'])

    @staticmethod
    def find_ingress_sg_rule(sg_rules: Dict[str, list]):
        # return {key: val['SecurityGroupRules'] for key, val in sg_rules.items()}
        out_dict = {}
        for k, v in sg_rules.items():
            for el in v:
                if not el['IsEgress']:
                    out_dict[k] = el['SecurityGroupRuleId']
        return out_dict

    def get_sg_rules(self, sg_id: str) -> dict:

        sg_rule = self.resource_obj.boto_client.describe_security_group_rules(
            Filters=[
                {
                    'Name': 'group-id',
                    'Values': [
                        sg_id
                    ]
                }
            ]
        )
        return sg_rule

    def check_for_default_sg(self) -> Dict[str, list]:
        out_dict = {}
        # return {sg.id: self.get_sg_rules(sg.id) for sg in self.resource_obj.sgs if sg.group_name == 'default'}
        for sg in self.resource_obj.sgs:
            if sg.group_name == 'default':
                sg_rule = self.get_sg_rules(sg.id)
                out_dict[sg.id] = sg_rule['SecurityGroupRules']
        return out_dict

    def revoke_ingress_sg_rule(self, sg_rules: Dict[str, str]):
        try:
            for k, v in sg_rules.items():
                logger.info("[!] Attempting to remove inbound SG rule '%s' in Region: '%s'",
                            v, self.resource_obj.region)
                self.resource_obj.boto_client.revoke_security_group_ingress(GroupId=k,
                                                                            SecurityGroupRuleIds=[v])
            return True
        except ClientError:
            raise

    def revoke_egress_sg_rule(self, sg_rules: Dict[str, str]):
        try:
            for k, v in sg_rules.items():
                logger.info("[!] Attempting to remove outbound SG rule '%s' in Region: '%s'",
                            v, self.resource_obj.region)
                self.resource_obj.boto_client.revoke_security_group_egress(GroupId=k,
                                                                           SecurityGroupRuleIds=[v])
            return True
        except ClientError:
            raise

    def revoke_sg_rules(self):
        default_sg = self.check_for_default_sg()
        # sg_egress_rules = self.find_egress_sg_rule(default_sg)
        if self.revoke_egress_sg_rule(self.find_egress_sg_rule(default_sg)):
            logger.info("[+] Outbound SG rule in Region: '%s' was successfully removed\n", self.resource_obj.region)
        # sg_ingress_rules = self.find_ingress_sg_rule(default_sg)
        if self.revoke_ingress_sg_rule(self.find_ingress_sg_rule(default_sg)):
            logger.info("[+] Inbound SG rule in Region: '%s' was successfully removed\n", self.resource_obj.region)
        return True

    # def update_sg_rules(self) -> bool:
    #     """Actions related to removing inbound/outbound rules from the default SG"""
    #     try:
    #         for sg in self.resource_obj.sgs:
    #             if sg.group_name == 'default':
    #                 sg_rule = self.get_sg_rules(sg.id)
    #                 for el in sg_rule['SecurityGroupRules']:
    #                     if el['IsEgress']:
    #                         logger.info("[!] Attempting to remove outbound SG rule '%s' in Region: '%s'",
    #                                     el['SecurityGroupRuleId'], self.resource_obj.region)
    #                         self.revoke_egress_sg_rule(sg.id, el['SecurityGroupRuleId'])
    #                         # self.resource_obj.boto_client.revoke_security_group_egress(GroupId=sg.id,
    #                         #                                                            SecurityGroupRuleIds=[
    #                         #                                                                el['SecurityGroupRuleId']])
    #                         logger.info("[+] Outbound SG rule '%s' in Region: '%s' was successfully removed\n",
    #                                     el['SecurityGroupRuleId'], self.resource_obj.region)
    #                     else:
    #                         logger.info("[!] Attempting to remove inbound SG rule '%s' in Region: '%s'",
    #                                     el['SecurityGroupRuleId'], self.resource_obj.region)
    #                         self.revoke_ingress_sg_rule(sg.id, el['SecurityGroupRuleId'])
    #                         # self.resource_obj.boto_client.revoke_security_group_ingress(GroupId=sg.id,
    #                         #                                                             SecurityGroupRuleIds=[
    #                         #                                                                 el['SecurityGroupRuleId']])
    #                         logger.info("[+] Inbound SG rule '%s' in Region: '%s' was successfully removed",
    #                                     el['SecurityGroupRuleId'], self.resource_obj.region)
    #     except ClientError:
    #         raise
    #     else:
    #         return True

    # def run_update(self) -> bool:
    #     """Method to execute other action methods on class and return True if all successful"""
    #     try:
    #         if self.update_nacl_rules() and self.update_sg_rules():
    #             return True
    #     except ClientError:
    #         raise


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
