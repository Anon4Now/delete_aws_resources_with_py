"""Module containing custom errors to raise"""


class NoDefaultVpcFoundError(Exception):
    """Raise this error when no default VPC is located"""
    pass
