from .utils import (
    create_logger,
    create_boto3_resource,
    create_boto3_client,
    error_handler,
    getArgs

)

from .default_resources import (
    Resources
)

logger = create_logger()
