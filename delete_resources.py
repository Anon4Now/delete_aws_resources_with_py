import logging
from botocore.exceptions import ClientError
from update_sgs_acls import UpdateResources


class DeleteResources:
    #  ---Class Attributes---

    # Logger configurations
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s: %(levelname)s: %(message)s')

    #  ---Class Methods---
    def __init__(self, ec2, vpcid, region):
        self.ec2 = ec2
        self.vpcid = vpcid
        self.region = region

        self.updateResource = UpdateResources(self.region)

    #  Delete the Internet Gateway(s) from Regions
    def deleteIGW(self):
        vpcResource = self.ec2.Vpc(self.vpcid)
        internetGateways = vpcResource.internet_gateways.all()

        # attempt to delete the resource(s)
        if internetGateways:
            for igw in internetGateways:
                try:
                    print(f'[*] Attempting to detach & remove IGW-ID: {igw.id}...')
                    igw.detach_from_vpc(
                        VpcId=self.vpcid
                    )
                    # Use the DryRun if test without deletion is needed
                    igw.delete(
                        # DryRun=True
                    )
                    DeleteResources.logger.info(f'[+] {igw.id} was successfully detached & removed\n')
                except ClientError:
                    DeleteResources.logger.exception(f'[-] Failed to delete Internet Gateway {igw.id}\n')
                    raise

    #  Delete the Subnet(s) associated with default VPC from regions
    def deleteSubnet(self):
        vpcResource = self.ec2.Vpc(self.vpcid)
        subnets = vpcResource.subnets.all()
        defaultSubnets = [self.ec2.Subnet(subnet.id) for subnet in subnets if subnet.default_for_az]

        # attempt to delete the resource(s)
        if defaultSubnets:
            try:
                for subnet in defaultSubnets:
                    print(f'[*] Attempting to remove Subnet: {subnet.id}')
                    # Use the DryRun if test without deletion is needed
                    subnet.delete(
                        # DryRun=True
                    )
                    DeleteResources.logger.info(f'[+] {subnet.id} was successfully removed\n')
            except ClientError:
                DeleteResources.logger.exception(
                    f'[-] Failed to delete Internet Gateway(s), please review manually...\n')
                raise

    #  Delete the Route Table(s) associated with default VPC from regions
    def deleteRouteTable(self):
        vpcResource = self.ec2.Vpc(self.vpcid)
        routeTables = vpcResource.route_tables.all()

        # attempt to delete the resource(s)
        if routeTables:
            try:
                for routeTable in routeTables:
                    #  found the route table associations
                    associatedAttribute = [routeTable.associations_attribute for routeTable in routeTables]
                    #  check to see if it is the default the route table, this cannot be removed
                    if [rtb_ass[0]['RouteTableId'] for rtb_ass in associatedAttribute if rtb_ass[0]['Main'] is True]:
                        print(f'[!] {routeTable.id} is the main route table, continue...\n')
                        continue
                    print(f'[*] Attempting to remove Route Table: {routeTable.id}')
                    table = self.ec2.RouteTable(routeTable.id)
                    # Use the DryRun if test without deletion is needed
                    table.delete(
                        # DryRun=True
                    )
                    DeleteResources.logger.info(f'[+] {routeTable.id} was successfully removed\n')
            except ClientError:
                DeleteResources.logger.exception(f'[-] Failed to delete Route Table(s), please review manually...\n')
                raise

    #  Delete the ACL(s) associated with default VPC from regions
    def deleteAcl(self, option):
        vpcResource = self.ec2.Vpc(self.vpcid)
        acls = vpcResource.network_acls.all()

        # attempt to delete the resource(s)
        if acls:
            try:
                for acl in acls:
                    #  check to see if the NACL is default, this cannot be removed
                    if acl.is_default:
                        if not option == "deleteOnlyOption":
                            print(f'[!] {acl.id} is the default NACL, attempting to remove default rules \n')
                            if self.updateResource.updateInboundNaclRule(acl.id):
                                print(f'[+] Ingress NACL Rule was removed for {acl.id}')
                            else:
                                print(f'[+] Failed to remove Ingress NACL Rule for {acl.id}')
                            if self.updateResource.updateOutboundNaclRule(acl.id):
                                print(f'[+] Egress NACL rule was remove for {acl.id}')
                            else:
                                print(f'[-] Failed to remove Egress rule for {acl.id}')
                            print(f'[!] Continuing Script \n')
                            continue
                        else:
                            print(f'[!] {acl.id} is the default NACL, taking no action and continuing \n')
                            continue
                    else:
                        if not option == "modifyOnlyOption":
                            print(f'[!] Attempting to remove ACL-ID {acl.id}')
                            acl.delete()
                            logger.info("[+] Successfully removed acl '%s'", acl.id)
            except ClientError as e:
                logger.error("[-] Failed to delete ACL(s), please review manually \n")

    #  Delete the Security Group(s) associated with default VPC from regions
    def deleteSecurityGroup(self, option):
        vpcResource = self.ec2.Vpc(self.vpcid)
        securityGroups = vpcResource.security_groups.all()

        # attempt to delete the resource(s)
        if securityGroups:
            try:
                for sg in securityGroups:
                    #  check to see if the NACL is default, this cannot be removed
                    if sg.group_name == 'default':
                        if not option == "deleteOnlyOption":
                            print(f'[!] {sg} is the default SG, attempting to remove default rules \n')
                            if self.updateResource.removeInboundSecurityGroupRule(sg.id):
                                print(f'[+] Ingress SG Rule was removed for {sg.id}')
                            else:
                                print(f'[+] Failed to remove Ingress SG Rule for {sg.id}')
                            if self.updateResource.removeOutboundSecurityGroupRule(sg.id):
                                print(f'[+] Egress SG rule was remove for {sg.id}')
                            else:
                                print(f'[-] Failed to remove Egress rule for {sg.id}')
                            print(f'[!] Continuing Script \n')
                            continue
                        else:
                            print(f'[!] {sg.id} is the default SG, taking no action and continuing \n')
                            continue
                    else:
                        if not option == "modifyOnlyOption":
                            print(f'[!] Attempting to remove SG-ID {sg.id}')
                            sg.delete()
                            logger.info("[+] Successfully removed SG '%s'", sg.id)
            except ClientError as e:
                logger.error("[-] Failed to delete Security Group(s), please review manually \n")

    #  Delete the VPC from regions
    def deleteVPC(self):
        vpcResource = self.ec2.Vpc(self.vpcid)

        # attempt to delete the resource(s)
        try:
            print(f'[*] Attempting to remove VPC-ID: {vpcResource.id}')
            # Use the DryRun if test without deletion is needed
            vpcResource.delete(
                # DryRun=True
            )
            DeleteResources.logger.info(f'[+] {vpcResource.id} was successfully removed\n')
        except ClientError:
            DeleteResources.logger.exception(f'[-] Failed to delete VPC {vpcResource.id}, please review manually...\n')
            raise
