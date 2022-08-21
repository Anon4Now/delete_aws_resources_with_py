import boto3
import json
import logging
from botocore.exceptions import ClientError


class UpdateResources:
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

    def __init__(self, region):
        self.region = region
        self.vpc_client = boto3.client("ec2", region_name=self.region)

    ########################################
    #                                      #
    #                                      #
    #         NETWORK ACL SECTION          #
    #                                      #
    #                                      #
    ########################################

    def updateInboundNaclRule(self, aclId):
        try:
            self.vpc_client.delete_network_acl_entry(
                Egress=False,
                NetworkAclId=aclId,
                RuleNumber=100
            )
        except ClientError as e:
            logger.error("[-] Failed to delete the default inbound NACL rule '%s', with error: %s", aclId, e)
            return False
        else:
            logger.info("[+] Successfully deleted the default inbound NACL rule: '%s'", aclId)
            return True

    def updateOutboundNaclRule(self, aclId):
        try:
            self.vpc_client.delete_network_acl_entry(
                Egress=True,
                NetworkAclId=aclId,
                RuleNumber=100
            )
        except ClientError as e:
            logger.error("[-] Failed to delete the default outbound NACL rule '%s', with error: %s", aclId, e)
            return False
        else:
            logger.info("[+] Successfully deleted the default outbound NACL rule: '%s'", aclId)

    ########################################
    #                                      #
    #                                      #
    #      SECURITY GROUP SECTION          #
    #                                      #
    #                                      #
    ########################################

    @staticmethod
    def returnSgrId(response, value):
        for key, val in response.items():
            if key == 'SecurityGroupRules':
                for x in range(len(val)):
                    if ('IsEgress', value) in val[x].items():
                        for key2, val2 in val[x].items():
                            if key2 == 'SecurityGroupRuleId':
                                return val2

    def getInboundSecurityGroupRuleId(self, sgId):
        sgRule = self.vpc_client.describe_security_group_rules(
            Filters=[
                {
                    'Name': 'group-id',
                    'Values': [
                        sgId
                    ]
                }
            ]
        )

        sgString = json.dumps(sgRule)
        response = json.loads(sgString)

        return self.returnSgrId(response, False)

    def getOutboundSecurityGroupRuleId(self, sgId):
        sgrule = self.vpc_client.describe_security_group_rules(
            Filters=[
                {
                    'Name': 'group-id',
                    'Values': [
                        sgId
                    ]
                }
            ]
        )

        sgString = json.dumps(sgrule)
        response = json.loads(sgString)

        return self.returnSgrId(response, True)

    def removeInboundSecurityGroupRule(self, sgId):
        sgrId = self.getInboundSecurityGroupRuleId(sgId)

        if sgrId and sgId:
            try:
                self.vpc_client.revoke_security_group_ingress(
                    GroupId=sgId,
                    SecurityGroupRuleIds=[
                        sgrId
                    ]
                )
            except ClientError as e:
                logger.error("[-] Failed to remove default inbound SG rule '%s' with error: %s", sgrId, e)
                return False
            else:
                logger.info("[+] Successfully removed default inbound SG rule '%s'", sgrId)
                return True

    def removeOutboundSecurityGroupRule(self, sgId):
        sgrId = self.getInboundSecurityGroupRuleId(sgId)

        if sgrId and sgId:
            try:
                self.vpc_client.revoke_security_group_egress(
                    GroupId=sgId,
                    SecurityGroupRuleIds=[
                        sgrId
                    ]
                )
            except ClientError as e:
                logger.error("[-] Failed to remove default outbound SG rule '%s' with error: %s", sgrId, e)
                return False
            else:
                logger.info("[+] Successfully removed default outbound SG rule '%s'", sgrId)
                return True
