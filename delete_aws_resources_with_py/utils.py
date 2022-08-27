"""Module containing Utility Functions"""

# Standard Library imports
import logging
import optparse
import sys
import os

# Third-party imports
import boto3
import botocore.exceptions


#####################################
# Get Environment Variables
#####################################
# REGION_LIST = os.environ.get("region_skip_list")  # use if needing to read from ENV vars

#####################################
# Create logger func
#####################################
def create_logger() -> logging:
    """
    Create a logger
    :return: logger
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
    log = logging.getLogger()
    # log.setLevel(logging.INFO)

    logging.getLogger('boto').setLevel(logging.CRITICAL)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    return log


logger = create_logger()  # create logger func


###########################
# Custom Error Handler func
###########################

def error_handler(func):
    # exception handling decorator function

    def inner_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except botocore.exceptions.NoCredentialsError as err:
            logger.error("NoCredentialsError: error=%s func=%s", err.fmt, func.__name__)
        except botocore.exceptions.NoRegionError as err:
            logger.error("NoRegionError: error=%s func=%s", err.fmt, func.__name__)
        except botocore.exceptions.ClientError as err:
            logger.error("ClientError: error=%s func=%s", err, func.__name__)
        except Exception as err:
            logger.error("GeneralException: error=%s func=%s", err, func.__name__)

    return inner_func


#######################################
# Option Parser
#######################################
parser = optparse.OptionParser()


def getArgs():
    parser.add_option("-d", "--delete", dest="sanitize_option", default=True)
    parser.add_option("-m", "--modify", dest="sanitize_option")
    parser.add_option("-h", "--help", dest="sanitize_option",
                      help="Use this flag to select an option to run against account (e.g. -d or --delete || -m or --modify --"
                           "The options available are below: "
                           "'delete' (default action)"
                           "- Deletes Internet Gateway"
                           "- Deletes Subnets"
                           "- Deletes Route Tables (not default)"
                           "- Deletes NACL (not default)"
                           "- Deletes SG (not default)"
                           "- Deletes default VPC"
                           "- Updates SSM parameter preferences to block public access"
                           "'modify'"
                           "- Updates default NACL (removes inbound/outbound rules)"
                           "- Updates default SG (removes inbound/outbound rules)"
                           "- Updates SSM parameter preferences to block public access")
    parsingInput = parser.parse_args()

    (options, args) = parsingInput

    if not options.sanitize_option:
        parser.error("[-] Please specify an option flag, --help for more info")
    else:
        return options


#######################################
# Boto Client or Resource creation func
#######################################

# TODO: UPDATE WITH SINGLE FUNC

def create_boto3_client(resource: str, region=None, access_key=None, secret_key=None, session_token=None):
    """
    Create a boto3 client based AWS resource (e.g. 'sts', 's3')
    :param resource: AWS resource passed as a string (required)
    :param region: AWS region passed as a string (optional)
    :param access_key: AWS STS Access Key string obtained for cross-account assume role actions (optional)
    :param secret_key: AWS STS Secret Key string obtained for cross-account assume role actions (optional)
    :param session_token: AWS STS Session Token string obtained for cross-account assume role actions (optional)
    :return: Initialized boto3 client
    :raise: AWS API "Boto3" returned client errors
    """
    try:
        boto_client = boto3.client(
            resource,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token
        )
        return boto_client
    except botocore.exceptions.ClientError as e:
        logger.error("[-] Failed to create boto client with error: %s", e)


def create_boto3_resource(resource: str, region=None, access_key=None, secret_key=None, session_token=None):
    """
    Create a boto3 resource based AWS resource (e.g. 'sts', 's3')
    :param resource: AWS resource passed as a string (required)
    :param region: AWS region passed as a string (optional)
    :param access_key: AWS STS Access Key string obtained for cross-account assume role actions (optional)
    :param secret_key: AWS STS Secret Key string obtained for cross-account assume role actions (optional)
    :param session_token: AWS STS Session Token string obtained for cross-account assume role actions (optional)
    :return: Initialized boto3 client
    :raise: AWS API "Boto3" returned client errors
    """
    try:
        boto_resource = boto3.resource(
            resource,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token
        )
        return boto_resource
    except botocore.exceptions.ClientError as e:
        logger.error("[-] Failed to create boto resource with error: %s", e)
