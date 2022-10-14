"""Module containing the class to delete resources"""

# Local App imports
from delete_aws_resources_with_py.default_resources import Resource
from delete_aws_resources_with_py.utils import logger, error_handler


class Delete:
    """Action-oriented class for deleting default resources"""

    def __init__(self, resource_obj: Resource) -> None:
        """
        Initializer that takes an instantiated Resource class object with VPC data.

        :param resource_obj: (required) Instantiated Resource object with necessary data
        """
        self.resource_obj = resource_obj

    def _delete_default_igw(self) -> bool:
        """
        Actions related to Internet Gateway deletion from default VPC.

        This method will take the current regions igw id and detach from the default VPC and then delete.
        :return A boolean result that represents whether the action was successfully completed

        :raise A Boto3 AWS ClientError that was created during the API call
        """

        for igw in self.resource_obj.igw:
            logger.info("[!] Attempting to detach and delete IGW-ID: '%s' in Region: '%s'", igw.id,
                        self.resource_obj.region)
            igw.detach_from_vpc(VpcId=self.resource_obj.vpc_id)
            igw.delete()
            logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", igw.id,
                        self.resource_obj.region)

        return True

    def _delete_default_subnet(self) -> bool:
        """
        Actions related to Subnet deletion from default VPC.

        This method will the current regions subnet id and loop through all created subnets
        in the default VPC. It will delete each found subnet.
        :return A boolean result that represents whether the action was successfully completed

        :raise A Boto3 AWS ClientError that was created during the API call
        """

        for subnet in self.resource_obj.subnet:
            logger.info("[!] Attempting to detach and delete Subnet-ID: '%s' in Region: '%s'", subnet.id,
                        self.resource_obj.region)
            subnet.delete()
            logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", subnet.id,
                        self.resource_obj.region)

        return True

    def _delete_default_rtb(self) -> bool:
        """
        Actions related to RouteTable deletion from default VPC; cannot delete the default RouteTable.

        This method will look at what the current regions route table(s) and determine
        if it is the 'Main' rtb, or if it is a custom rtb. If it is custom it will delete, and
        if it is the 'Main' rtb it will be skipped.
        :return A boolean result that represents whether the action was successfully completed

        :raise A Boto3 AWS ClientError that was created during the API call
        """
        for route_table in self.resource_obj.route_table:
            #  found the route table associations
            associated_attribute = [routeTable.associations_attribute for routeTable in
                                    self.resource_obj.route_table]
            #  check to see if it is the default the route table, this cannot be removed
            if [rtb_ass[0]['RouteTableId'] for rtb_ass in associated_attribute if rtb_ass[0]['Main'] is True]:
                logger.info("[!] '%s'' is the main route table, this cannot be removed continuing\n",
                            route_table.id)
                continue
            logger.info("[!] Attempting to detach and delete RTB: '%s' in Region: '%s'", route_table.id,
                        self.resource_obj.region)
            self.resource_obj.boto_resource.RouteTable(route_table.id).delete()
            logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", route_table.id,
                        self.resource_obj.region)

        return True

    def _delete_default_nacl(self) -> bool:
        """
        Actions related to NACL deletion from default VPC; cannot delete the default NACL.

        This method will look at the current regions NACL(s) and determine whether
        the NACL is the default VPC NACL or a custom NACL. If it is a custom NACL it will be
        deleted, if it is the default VPC NACL it will be skipped.
        :return A boolean result that represents whether the action was successfully completed

        :raise A Boto3 AWS ClientError that was created during the API call
        """

        for acl in self.resource_obj.acl:
            if not acl.is_default:
                logger.info("[!] Attempting to remove NACL-ID: '%s' for Region: '%s'", acl.id,
                            self.resource_obj.region)
                acl.delete()
                logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", acl.id,
                            self.resource_obj.region)
            logger.info("[!] '%s' is the default NACL, this cannot be removed continuing\n", acl.id)
            continue

        return True

    def _delete_default_sg(self) -> bool:
        """
        Actions related to SG deletion from default VPC; cannot delete the default SG.

        This method will look at the current regions SG(s) and determine whether
        the SG is the default VPC SG or a custom SG. If it is a custom SG it will be
        deleted, if it is the default VPC SG it will be skipped.
        :return A boolean result that represents whether the action was successfully completed

        :raise A Boto3 AWS ClientError that was created during the API call
        """

        for sg in self.resource_obj.sgs:
            if sg.group_name != 'default':
                logger.info("[!] Attempting to remove SG-ID: '%s' for Region: '%s'", sg.id,
                            self.resource_obj.region)
                sg.delete()
                logger.info("[+] '%s' in Region: '%s' was successfully detached and deleted\n", sg.id,
                            self.resource_obj.region)
            logger.info("[!] '%s' is the default SG, this cannot be removed continuing\n", sg.id)
            continue

        return True

    def _delete_default_vpc(self) -> bool:
        """
        Actions related to the deletion of the default VPC.

        This method performs the actual deletion of the default VPC and needs to be
        the last method called to avoid errors with resources still existing
        (excluding default NACL, SG, and RTB).
        :return A boolean result that represents whether the action was successfully completed

        :raise A Boto3 AWS ClientError that was created during the API call
        """

        logger.info("[!] Attempting to remove VPC-ID: '%s' for Region: '%s'", self.resource_obj.vpc_id,
                    self.resource_obj.region)
        self.resource_obj.current_vpc_resource.delete()
        logger.info("[+] Default VPC in Region: '%s' was successfully detached and deleted\n",
                    self.resource_obj.region)

        return True

    @error_handler
    def delete_resources(self) -> bool:
        """
        Method to run all the action methods and return True if all successful.

        This is the main method called that handles all the calls to the
        other methods in the order necessary to perform the default VPC
        deletion step.
        :return A boolean result that represents whether all method calls were successfully completed

        :raise A Boto3 AWS ClientError that was created during the API call
        """
        self._delete_default_igw()
        self._delete_default_subnet()
        self._delete_default_rtb()
        self._delete_default_nacl()
        self._delete_default_sg()
        self._delete_default_vpc()
        return True
