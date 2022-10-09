"""Module containing functions to change SSM preferences to private"""
from typing import Any

# Local App imports
from delete_aws_resources_with_py.utils import logger


def get_current_service_setting(ssm_client: Any, share_setting: str) -> str:
    """Check to see what the current service setting is."""

    return ssm_client.get_service_setting(SettingId=share_setting)['ServiceSetting']['SettingValue']


def update_public_service_setting(ssm_client: Any, share_setting: str, share_setting_status: str) -> int:
    """Make changes to the share service setting"""
    return ssm_client.update_service_setting(SettingId=share_setting, SettingValue=share_setting_status)['ResponseMetadata']['HTTPStatusCode']


def update_ssm_preferences(boto_client, region) -> None:
    """
    Function designed to check the SSM document preferences in each region.
    If they are open to the public, update the preference to be private to the account.
    :param boto_client: (required) Instantiated boto3 client for the current region in the loop
    :param region: (required) Current region in the loop passed from main()
    :return: Boolean depicting the success of the actions (True = success/False = failure)
    """
    public_share_setting = "/ssm/documents/console/public-sharing-permission"  # path provided by BOTO3 API docs
    status = 200
    current_setting = get_current_service_setting(boto_client, public_share_setting)
    if current_setting != 'Enable':
        logger.info("[+] SSM Document preferences already block public access with status '%s', no action taken\n",
                    current_setting)
        return

    logger.info(
        "[!] SSM Document preferences allows public access with status '%s' in Region: '%s', attempting to update",
        current_setting, region)
    if update_public_service_setting(boto_client, public_share_setting, 'Disable') == status:
        logger.info("[+] Preferences successfully updated to 'Disable' in Region: '%s'\n", region)
