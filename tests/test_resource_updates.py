"""Module containing tests for Delete and Update classes"""

import pytest

# Local App imports
from delete_aws_resources_with_py.resource_updates import (
    Delete,
    Update
)


def test_delete_class(get_resource_obj):
    del_res = Delete(get_resource_obj)
    assert del_res.run_delete() is True


def test_update_class_nacl_rules(get_resource_obj):
    update_res = Update(get_resource_obj)
    assert update_res.update_nacl_rules() is True


@pytest.mark.skip(reason="describe_security_group_rules doesn't exist in moto yet, can't mock")
def test_update_class_sg_rules(get_resource_obj):
    update_res = Update(get_resource_obj)
    assert update_res.update_sg_rules() is True


@pytest.mark.skip(reason="get_service_setting & update_service_setting doesn't exist in moto yet, can't mock")
def test_update_ssm_preferences(ec2_client):
    assert Update.update_ssm_preferences(ec2_client, region='us-east-1')


@pytest.mark.skip(reason="going to fail due to missing moto services")
def test_run_update(get_resource_obj):
    update_res = Update(get_resource_obj)
    assert update_res.run_update() is True
