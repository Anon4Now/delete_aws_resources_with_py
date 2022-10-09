"""Module containing functions to change SSM preferences to private"""
from typing import Any

# Local App imports
from delete_aws_resources_with_py.utils import logger


class SsmPreference:
    def __init__(self, ssm_client: Any, region: str) -> None:
        self.ssm_client = ssm_client
        self.region = region
        self.public_share_setting = "/ssm/documents/console/public-sharing-permission"

    def __repr__(self):
        return f'SsmPreference({self.ssm_client}, {self.region})'  # pragma: no cover

    def get_current_service_setting_check(self) -> bool:
        """Check to see what the current service setting is."""
        return self.ssm_client.get_service_setting(SettingId=self.public_share_setting)['ServiceSetting'][
                   'SettingValue'] == 'Enable'  # pragma: no cover - moto mock not implemented

    def update_public_service_setting_check(self, share_setting_status: str) -> bool:
        """Make changes to the share service setting"""
        return self.ssm_client.update_service_setting(
            SettingId=self.public_share_setting,
            SettingValue=share_setting_status)['ResponseMetadata']['HTTPStatusCode'] \
            == 200  # pragma: no cover - moto mock not implemented

    def check_ssm_preferences(self) -> None:
        """
        Function designed to check the SSM document preferences in each region.
        If they are open to the public, update the preference to be private to the account.

        """

        if not self.get_current_service_setting_check():
            logger.info(
                "[+] SSM Document preferences already block public access with status 'Disable', no action taken\n")
            return
        logger.info(
            "[!] SSM Document preferences allows public access with status 'Enable' in Region: '%s', attempting to update",
            self.region)
        if self.update_public_service_setting_check:
            logger.info("[+] Preferences successfully updated to 'Disable' in Region: '%s'\n", self.region)
            return
