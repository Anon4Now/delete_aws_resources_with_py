import boto3
import logging
from botocore.exceptions import ClientError


class UpdateSSMResource:
    logger = logging.getLogger()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

    def __init__(self, region):
        self.region = region
        self.ssmClient = boto3.client("ssm", region_name=self.region)

    def getSsmSettings(self):
        pass

    def updateSsmSettings(self):

        try:
            self.ssmClient.update_service_setting(
                SettingId="/ssm/documents/console/public-sharing-permission",
                SettingValue="Disable"
            )
        except ClientError as e:
            logger.error("[-] Failed to update the SSM access settings for region: '%s' with error: %s", self.region, e)
        else:
            logger.info("[+] Successfully update the SSM access settings for region: '%s'", self.region)
