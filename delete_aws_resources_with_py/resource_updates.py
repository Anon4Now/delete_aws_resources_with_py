"""Module that contains classes for updating resources."""

# Standard Library imports
from typing import Any, Dict
from abc import ABC, abstractmethod

# Third-party imports
from botocore.exceptions import ClientError

# Local App imports
from delete_aws_resources_with_py.default_resources import Resource
from delete_aws_resources_with_py.utils import logger


class UpdateResource(ABC):
    """Abstract Class meant to be inherited."""

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
    def find_egress_sg_rule(sg_rules: Dict[Any, list]) -> Dict['str', 'str']:
        """
        Static method that generates a dict containing the SG egress rule(s).

        :param sg_rules: (required) A dict that contains any type of key (usually a str) and a string val
        :return: A dict that contains the Security Group ID and the Security Group Rule ID both as strings
        """
        return {k: el['SecurityGroupRuleId'] for k, v in sg_rules.items() for el in v if el['IsEgress']}

    @staticmethod
    def find_ingress_sg_rule(sg_rules: Dict[Any, list]):
        """
        Static method that generates a dict containing the SG ingress rule(s).

        :param sg_rules: (required) A dict that contains any type of key (usually a str) and a string val
        :return: A dict that contains the Security Group ID and the Security Group Rule ID both as strings
        """
        return {k: el['SecurityGroupRuleId'] for k, v in sg_rules.items() for el in v if not el['IsEgress']}

    def get_sg_rules(self, sg_id: str) -> Dict[str, Any]:
        """
        Method that calls the AWS API to get a list of the Security Group rules.

        :param sg_id: (required) A string that contains the Security Group ID used to get the SG rule ID's
        :return: A dict that contains a complex structure (i.e. {'something': [{'something_else: 1}])
        """

        return self.resource_obj.boto_client.describe_security_group_rules(
            Filters=[{'Name': 'group-id', 'Values': [sg_id]}])

    def check_for_default_sg(self) -> Dict[Any, Any]:
        """
        Method used to filter for default Security Groups in VPC.

        :return: A dict containing complex structure (i.e. {'something': [{'something_else: 1}])
        """
        out_dict = {}
        for sg in self.resource_obj.sgs:
            if sg.group_name == 'default':
                sg_rule = self.get_sg_rules(sg.id)
                out_dict[sg.id] = sg_rule['SecurityGroupRules']
        return out_dict

    def revoke_ingress_sg_rule(self, sg_rules: Dict[str, str]) -> bool:
        """
        A method for deleting the default Security Group ingress rule(s).

        :param sg_rules: (required) A dict containing the Security Group ID and Security Group Rule ID as strings
        :return: A boolean that represents whether the deletion event was successful

        :raise A Boto3 API ClientError created by AWS during the API call
        """
        try:
            for k, v in sg_rules.items():
                logger.info("[!] Attempting to remove inbound SG rule '%s' in Region: '%s'",
                            v, self.resource_obj.region)
                self.resource_obj.boto_client.revoke_security_group_ingress(GroupId=k,
                                                                            SecurityGroupRuleIds=[v])
            return True
        except ClientError:
            raise

    def revoke_egress_sg_rule(self, sg_rules: Dict[str, str]) -> bool:
        """
        A method for deleting the default Security Group egress rule(s).

        :param sg_rules: (required) A dict containing the Security Group ID and Security Group Rule ID as strings
        :return: A boolean that represents whether the deletion event was successful

        :raise A Boto3 API ClientError created by AWS during the API call
        """
        try:
            for k, v in sg_rules.items():
                logger.info("[!] Attempting to remove outbound SG rule '%s' in Region: '%s'",
                            v, self.resource_obj.region)
                self.resource_obj.boto_client.revoke_security_group_egress(GroupId=k,
                                                                           SecurityGroupRuleIds=[v])
            return True
        except ClientError:
            raise

    def revoke_sg_rules(self) -> bool:
        """
        Main method that will call the other class methods in necessary order to complete script.

        :return: Boolean result the represents whether the actions were successfully completed
        """
        default_sg = self.check_for_default_sg()
        if self.revoke_egress_sg_rule(self.find_egress_sg_rule(default_sg)):
            logger.info("[+] Outbound SG rule in Region: '%s' was successfully removed\n", self.resource_obj.region)
        if self.revoke_ingress_sg_rule(self.find_ingress_sg_rule(default_sg)):
            logger.info("[+] Inbound SG rule in Region: '%s' was successfully removed\n", self.resource_obj.region)
        return True
