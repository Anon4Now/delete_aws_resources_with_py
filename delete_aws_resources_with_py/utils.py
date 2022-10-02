"""Module containing Utility Functions"""

# Standard Library imports
import logging
import optparse

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
    parsingInput = parser.parse_args()

    (options, args) = parsingInput

    if not options.sanitize_option:
        parser.error("[-] Please specify an option flag, --help for more info")
    else:
        return options


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
    if boto_type not in ['boto_client', 'boto_resource']:
        logger.error(
            "[-] boto_type param passed to create_boto3 not valid, can either be 'boto_client' or 'boto_resource'")
    else:
        if boto_type == 'boto_client':
            boto_client = boto3.client(
                service,
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token
            )
            return boto_client
        else:
            boto_resource = boto3.resource(
                service,
                region_name=region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token
            )
        return boto_resource
