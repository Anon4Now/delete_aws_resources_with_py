"""Module containing the class to delete resources"""

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
            logger.info("[+] Default VPC in Region: '%s' was successfully detached and deleted",
                        self.resource_obj.region)
        except ClientError:
            raise
        else:
            return True

    def delete_resources(self) -> bool:
        """Method to run all the action methods and return True if all successful"""
        try:
            self.delete_default_igw()
            self.delete_default_subnet()
            self.delete_default_rtb()
            self.delete_default_nacl()
            self.delete_default_sg()
            self.delete_default_vpc()
            return True
        except ClientError:
            raise