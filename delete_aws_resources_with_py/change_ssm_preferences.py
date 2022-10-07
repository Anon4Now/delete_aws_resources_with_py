"""Module containing functions to change SSM preferences to private"""

# Local App imports
from delete_aws_resources_with_py.utils import logger


def update_ssm_preferences(boto_client, region) -> None:
    """
    Function designed to check the SSM document preferences in each region.
    If they are open to the public, update the preference to be private to the account.
    :param boto_client: (required) Instantiated boto3 client for the current region in the loop
    :param region: (required) Current region in the loop passed from main()
    :return: Boolean depicting the success of the actions (True = success/False = failure)
    """
    public_share_setting = "/ssm/documents/console/public-sharing-permission"  # path provided by BOTO3 API docs
    get_current_acct_settings = boto_client.get_service_setting(
        SettingId=public_share_setting)  # check current setting
    current_setting = get_current_acct_settings['ServiceSetting']['SettingValue']
    if current_setting == 'Enable':
        logger.info(
            "[!] SSM Document preferences allows public access with status '%s' in Region: '%s', attempting to update",
            current_setting, region)
        boto_client.update_service_setting(SettingId=public_share_setting, SettingValue="Disable")  # update setting
        logger.info("[+] Preferences successfully updated to 'Disable' in Region: '%s'\n", region)
    else:
        logger.info("[+] SSM Document preferences already block public access with status '%s', no action taken\n",
                    current_setting)
