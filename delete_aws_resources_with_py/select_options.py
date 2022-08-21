from get_resources import GetVPCS
from delete_resources import DeleteResources
from update_ssm_doc_access import UpdateSSMResource
import logging


class SetArgsAndObjects:
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

    def __init__(self, client, ec2, region):
        self.vpcClient = client
        self.vpcResources = GetVPCS(self.vpcClient)
        self.vpcs = self.vpcResources.getDefaultVpcs()

        self.ec2 = ec2
        self.region = region
        self.updateSsm = UpdateSSMResource(self.region)

    def deleteResourceOption(self):
        for vpc in self.vpcs:
            deleted = DeleteResources(self.ec2, vpc, self.region)
            print(f'''
    ********************************
    
        Region: {self.region}
        VPC-ID: {vpc}
        
    ********************************
    ''')

            print(f">> PERFORMING ONLY DELETE OPTION ACTIONS <<\n")

            deleted.deleteIGW()
            deleted.deleteSubnet()
            deleted.deleteRouteTable()
            deleted.deleteAcl("deleteOnlyOption")
            deleted.deleteSecurityGroup("deletedOnlyOption")
            deleted.deleteVPC()

    def modifyResourceOption(self):

        for vpc in self.vpcs:
            deleted = DeleteResources(self.ec2, vpc, self.region)
            print(f'''
                ********************************

                    Region: {self.region}
                    VPC-ID: {vpc}

                ********************************
                ''')

            print(f">> PERFORMING ONLY MODIFY OPTION ACTIONS <<\n")

            deleted.deleteAcl("modifyOnlyOption")
            deleted.deleteSecurityGroup("modifyOnlyOption")

        if self.updateSsm.updateSsmSettings():
            logger.info("[+] Successfully updated Region '%s' SSM settings for non-public access", self.region)
            logger.info("<=================================================================>")
        else:
            logger.error("[-] Failed to update Region '%s' SSM settings for non-public access", self.region)

    def allOptions(self):
        for vpc in self.vpcs:
            deleted = DeleteResources(self.ec2, vpc, self.region)
            print(f'''
        ********************************

            Region: {self.region}
            VPC-ID: {vpc}

        ********************************
        ''')

            print(f">> PERFORMING ALL OPTION ACTIONS <<\n")

            deleted.deleteIGW()
            deleted.deleteSubnet()
            deleted.deleteRouteTable()
            deleted.deleteAcl("allOptions")
            deleted.deleteSecurityGroup("allOptions")
            deleted.deleteVPC()
        if self.updateSsm.updateSsmSettings():
            logger.info("[+] Successfully updated Region '%s' SSM settings for non-public access", self.region)
            logger.info("<=================================================================>")
        else:
            logger.error("[-] Failed to update Region '%s' SSM settings for non-public access", self.region)
