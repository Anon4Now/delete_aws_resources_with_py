"""Module containing functions to change SSM preferences to private."""

# Standard Library imports
from typing import Any

# Local App imports
from delete_aws_resources_with_py.utils import logger


class SsmPreference:
    """Action-oriented class to check and update the region SSM settings."""
    def __init__(self, ssm_client: Any, region: str) -> None:
        """
        Initializer that takes in two params.

        :param ssm_client: (required) An instantiated boto3 client for SSM
        :param region: (required) A string value containing the current region
        """
        self.ssm_client = ssm_client
        self.region = region
        self.public_share_setting = "/ssm/documents/console/public-sharing-permission"

    def __repr__(self):
        return f'SsmPreference({self.ssm_client}, {self.region})'  # pragma: no cover

    def _get_current_service_setting_check(self) -> bool:
        """
        Check to see what the current service setting is.

        :return A boolean result that represents if the region already has blocked access
        """
        return self.ssm_client.get_service_setting(SettingId=self.public_share_setting)['ServiceSetting'][
                   'SettingValue'] == 'Enable'

    def _update_public_service_setting_check(self, share_setting_status: str) -> bool:
        """
        Make changes to the share service setting in region.

        :param share_setting_status: (required) A string value containing the status value to be passed in API call
        :return A boolean result that represents whether the change occurred successfully
        """
        return self.ssm_client.update_service_setting(
            SettingId=self.public_share_setting,
            SettingValue=share_setting_status)['ResponseMetadata']['HTTPStatusCode'] \
            == 200

    def check_ssm_preferences(self) -> None:
        """
        Function designed to check the SSM document preferences in each region.

        If they are open to the public, update the preference to be private to the account.
        :return None

        """

        if not self._get_current_service_setting_check():
            logger.info(
                "[+] SSM Document preferences already block public access with status 'Disable', no action taken\n")
            return
        logger.info(
            "[!] SSM Document preferences allows public access with status 'Enable' in Region: '%s', attempting to update",
            self.region)
        if self._update_public_service_setting_check('Disable'):
            logger.info("[+] Preferences successfully updated to 'Disable' in Region: '%s'\n", self.region)
            return
