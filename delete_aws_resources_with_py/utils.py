"""Module containing Utility Functions"""
import json
# Standard Library imports
import logging
import optparse

# Third-party imports
import boto3
import botocore.exceptions

#####################################
# Get Environment Variables
#####################################
with open('config.json', 'r') as f:
    data = json.load(f)

SKIP_REGION_LIST = data.get('skip_regions')


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
    """Function used to handle exceptions from other funcs/methods"""

    def inner_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except botocore.exceptions.ClientError as err:
            logger.error("ClientError: error=%s func=%s", err, func.__name__)
        except Exception as err:
            logger.error("GeneralException: error=%s func=%s", err, func.__name__)

    return inner_func


#######################################
# Option Parser
#######################################
parser = optparse.OptionParser()


def get_args() -> str:
    """Function used to trigger and handle CLI args passed by user"""
    parser.add_option(
        "-o",
        "--option",
        dest="sanitize_option",
        help="Requires either (delete OR modify)"
             "** delete option **\n"
             "- Deletes Internet Gateway"
             "- Deletes Subnets"
             "- Deletes Route Tables (not default)"
             "- Deletes NACL (not default)"
             "- Deletes SG (not default)"
             "- Deletes default VPC"
             "- Updates SSM parameter preferences to block public access\n\n"
             "** modify option **\n"
             "- Updates default NACL (removes inbound/outbound rules)"
             "- Updates default SG (removes inbound/outbound rules)"
             "- Updates SSM parameter preferences to block public access"
    )
    parsing_input = parser.parse_args()

    (options, args) = parsing_input

    if not options.sanitize_option:
        parser.error("[-] Please specify an option flag, --help for more info")
    else:
        return options.sanitize_option


#######################################
# Boto Client or Resource creation func
#######################################

@error_handler
def create_boto3(service: str, boto_type: str, region=None, access_key=None, secret_key=None, session_token=None):
    """
    Create a boto3 client or resource based AWS service passed (e.g. 'sts', 's3')
    :param service: (required) AWS resource passed as a string (e.g. 'sts', 'ssm', 'ec2', etc...)
    :param boto_type: (required) Type of boto3 instantiation wanted (i.e. 'boto_client' OR 'boto_resource')
    :param region: (optional) AWS region passed as a string (optional)
    :param access_key: (optional) AWS STS Access Key string obtained for cross-account assume role actions (optional)
    :param secret_key: (optional) AWS STS Secret Key string obtained for cross-account assume role actions (optional)
    :param session_token: (optional) AWS STS Session Token string obtained for cross-account assume role actions (optional)
    :return: Initialized boto3 client or resource
    """
    if boto_type == 'boto_client':
        return boto3.client(service, region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, aws_session_token=session_token)

    elif boto_type == 'boto_resource':
        return boto3.resource(service, region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, aws_session_token=session_token)

    else:
        logger.error(
            "[-] boto_type param passed to create_boto3 not valid, can either be 'boto_client' or 'boto_resource'")
