"""Module containing tests for Delete and Update classes"""

# Local App imports
from delete_aws_resources_with_py.resource_updates import (
    UpdateNaclResource,
    UpdateSgResource
)
from delete_aws_resources_with_py.main import execute_changes_on_resources


def test_update_class_nacl_rules(get_resource_obj):
    update_res = UpdateNaclResource(get_resource_obj)
    assert update_res.update_nacl_rules() is True


# def test_update_sg_rules(get_resource_obj, mocker, egress_rule, ssm_client):
#     def mock_get_sg_rules(*args, **kwargs):
#         return egress_rule
#
#     mocker.patch('delete_aws_resources_with_py.main.UpdateSgResource.get_sg_rules', mock_get_sg_rules)
#
#     def mock_revoke_sg_rule(*args, **kwargs):
#         return {'Return': True}
#
#     mocker.patch('delete_aws_resources_with_py.main.UpdateSgResource.revoke_ingress_sg_rule', mock_revoke_sg_rule)
#     mocker.patch('delete_aws_resources_with_py.main.UpdateSgResource.revoke_egress_sg_rule', mock_revoke_sg_rule)
#
#     actual = execute_changes_on_resources('modify', get_resource_obj, ssm_client, 'us-east-1')
#     assert actual is True
