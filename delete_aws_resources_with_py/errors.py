"""Module containing custom errors"""


class UserArgNotFoundError(Exception):
    """Raise this when modify/delete are not passed in CLI"""
    pass


class NoDefaultVpcExistsError(Exception):
    """Raise when there are no default VPC's in a region"""
    pass
