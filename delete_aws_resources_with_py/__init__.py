from .utils import (
    create_boto3_resource,
    create_boto3_client,
    error_handler,
    create_logger
)

from .default_resources import (
    AlterResources
)

logger = create_logger()

logger.info("[-] gusdusgus")