"""Module containing tests for SsmPreference class."""

from delete_aws_resources_with_py.change_ssm_preferences import SsmPreference


def test_get_current_service_setting(ssm_client, mocker):
    """Test getting the current service setting"""

    def mock_get_current_service_setting(*args, **kwargs):
        return {}

    mocker.patch('tests.test_change_ssm_preferences.SsmPreference.get_current_service_setting_check',
                 mock_get_current_service_setting)

    assert SsmPreference(ssm_client, 'us-east-1').get_current_service_setting_check() == {}


def test_ssm_preference_class_enable_block(ssm_client, mocker):
    """Test the class to update the preferences."""

    def mock_get_current_service_setting(*args):
        return True

    mocker.patch('delete_aws_resources_with_py.main.SsmPreference.get_current_service_setting_check',
                 mock_get_current_service_setting)

    def mock_update_public_service_setting(*args):
        return True

    mocker.patch('delete_aws_resources_with_py.main.SsmPreference.update_public_service_setting_check',
                 mock_update_public_service_setting)

    assert SsmPreference(ssm_client, 'us-east-1').check_ssm_preferences() is None


def test_ssm_preference_class_no_block(ssm_client, mocker):
    def mock_get_current_service_setting(*args):
        return False

    mocker.patch('delete_aws_resources_with_py.main.SsmPreference.get_current_service_setting_check',
                 mock_get_current_service_setting)

    assert SsmPreference(ssm_client, 'us-east-1').check_ssm_preferences() is None
