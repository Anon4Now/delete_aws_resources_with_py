"""Module containing tests for main module in script."""
import pytest
from collections import namedtuple

from delete_aws_resources_with_py.main import (
    main,
    execute_changes_on_resources,
    check_user_arg_response,
    get_region_list,
    create_boto_objects
)
from delete_aws_resources_with_py.errors import UserArgNotFoundError, NoDefaultVpcExistsError

from delete_aws_resources_with_py.default_resources import Resource


def test_check_user_arg_response():
    with pytest.raises(UserArgNotFoundError):
        check_user_arg_response('hello')

    assert check_user_arg_response('delete') is True
    assert check_user_arg_response('modify') is True


def test_get_region_list(mocker, ec2_client):
    expected = ['af-south-1', 'ap-east-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-south-1',
                'ap-southeast-1', 'ap-southeast-2', 'ap-southeast-3', 'ca-central-1', 'eu-central-1', 'eu-north-1',
                'eu-south-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'me-south-1', 'sa-east-1', 'us-east-2',
                'us-west-1', 'us-gov-east-1', 'us-gov-west-1', 'cn-north-1', 'cn-northwest-1']

    def mock_create_boto3():
        return ec2_client.describe_regions()

    mocker.patch('delete_aws_resources_with_py.main.get_region_list', mock_create_boto3)

    assert get_region_list() == expected


def test_create_boto_objects(mocker):
    def mock_create_boto3(*args, **kwargs):
        return {}

    mocker.patch('delete_aws_resources_with_py.main.create_boto3', mock_create_boto3)

    assert create_boto_objects('us-east-1') == ({}, {}, {})


def test_execute_changes_on_resources(ec2_client, ec2_resource, mocker, sg_egress_ingress_rule):
    def mock_get_sg_rules(*args, **kwargs):
        return sg_egress_ingress_rule

    mocker.patch('delete_aws_resources_with_py.main.UpdateSgResource._get_sg_rules', mock_get_sg_rules)

    def mock_revoke_sg_rule(*args, **kwargs):
        return {'Return': True}

    mocker.patch('delete_aws_resources_with_py.main.UpdateSgResource._revoke_ingress_sg_rule', mock_revoke_sg_rule)
    mocker.patch('delete_aws_resources_with_py.main.UpdateSgResource._revoke_egress_sg_rule', mock_revoke_sg_rule)

    obj = Resource(ec2_resource, ec2_client, 'us-east-1')
    assert execute_changes_on_resources(obj, 'modify') is True
    assert execute_changes_on_resources(obj, 'delete') is True
    with pytest.raises(NoDefaultVpcExistsError):
        assert execute_changes_on_resources(obj, 'delete') is True


def test_main_func_works(ec2_client, ec2_resource, ssm_client, mocker):
    def mock_get_current_service_setting(*args):
        return True

    mocker.patch('delete_aws_resources_with_py.main.SsmPreference._get_current_service_setting_check',
                 mock_get_current_service_setting)

    def mock_update_public_service_setting(*args):
        return True

    mocker.patch('delete_aws_resources_with_py.main.SsmPreference._update_public_service_setting_check',
                 mock_update_public_service_setting)

    def mock_get_args():
        return 'delete'

    mocker.patch('delete_aws_resources_with_py.main.get_args', mock_get_args)

    def mock_get_regions():
        return ec2_client.describe_regions()

    mocker.patch('delete_aws_resources_with_py.main.get_region_list', mock_get_regions)

    def mock_create_boto_objects(*args):
        test = namedtuple('test', ['ssm_client', 'ec2_resource', 'ec2_client'])
        t = test(ssm_client, ec2_resource, ec2_client)
        return t

    mocker.patch('delete_aws_resources_with_py.main.create_boto_objects', mock_create_boto_objects)

    assert main() is None


def test_main_func_raises_bad_arg(ec2_client, ec2_resource, ssm_client, mocker):
    def mock_get_args():
        return 'anything'

    mocker.patch('delete_aws_resources_with_py.main.get_args', mock_get_args)

    def mock_check_user_arg_response(*args):
        return False

    mocker.patch('delete_aws_resources_with_py.main.check_user_arg_response', mock_check_user_arg_response)

    with pytest.raises(UserArgNotFoundError):
        main()
