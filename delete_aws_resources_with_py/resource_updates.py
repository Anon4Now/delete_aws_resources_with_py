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
        self.resource_obj = resource_obj  # pragma: no cover - this is an abstractmethod


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

    @staticmethod
    def find_ingress_sg_rule(sg_rules: Dict[str, list]):
        # return {key: val['SecurityGroupRules'] for key, val in sg_rules.items()}
        out_dict = {}
        for k, v in sg_rules.items():
            for el in v:
                if not el['IsEgress']:
                    out_dict[k] = el['SecurityGroupRuleId']
        return out_dict

    def get_sg_rules(self, sg_id: str) -> dict:  # pragma: no cover - moto not created yet

        return self.resource_obj.boto_client.describe_security_group_rules(Filters=[{'Name': 'group-id', 'Values': [sg_id]}])

    def check_for_default_sg(self) -> Dict[str, list]:
        out_dict = {}
        # return {sg.id: self.get_sg_rules(sg.id) for sg in self.resource_obj.sgs if sg.group_name == 'default'}
        for sg in self.resource_obj.sgs:
            if sg.group_name == 'default':
                sg_rule = self.get_sg_rules(sg.id)
                out_dict[sg.id] = sg_rule['SecurityGroupRules']
        return out_dict

    def revoke_ingress_sg_rule(self, sg_rules: Dict[str, str]):  # pragma: no cover - not able to test this API call due to the mocking of the VPC
        try:
            for k, v in sg_rules.items():
                logger.info("[!] Attempting to remove inbound SG rule '%s' in Region: '%s'",
                            v, self.resource_obj.region)
                self.resource_obj.boto_client.revoke_security_group_ingress(GroupId=k,
                                                                            SecurityGroupRuleIds=[v])
            return True
        except ClientError:
            raise

    def revoke_egress_sg_rule(self, sg_rules: Dict[str, str]):  # pragma: no cover - not able to test this API call due to the mocking of the VPC
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
        if self.revoke_egress_sg_rule(self.find_egress_sg_rule(default_sg)):
            logger.info("[+] Outbound SG rule in Region: '%s' was successfully removed\n", self.resource_obj.region)
        if self.revoke_ingress_sg_rule(self.find_ingress_sg_rule(default_sg)):
            logger.info("[+] Inbound SG rule in Region: '%s' was successfully removed\n", self.resource_obj.region)
        return True
