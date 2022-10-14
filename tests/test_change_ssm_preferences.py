"""Module containing tests for SsmPreference class."""

from delete_aws_resources_with_py.change_ssm_preferences import SsmPreference


def test_get_current_service_setting(ssm_client, fake_boto_client):
    obj = SsmPreference(fake_boto_client, 'us-east-1')
    assert obj._get_current_service_setting_check() is True
    assert obj._update_public_service_setting_check('Disable') is True
    assert obj.check_ssm_preferences() is None
