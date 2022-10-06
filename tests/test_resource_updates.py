"""Module containing tests for Delete and Update classes"""

# Local App imports
from delete_aws_resources_with_py.resource_updates import (
    Delete,
    Update
)
from delete_aws_resources_with_py.main import execute_changes_on_resources


def test_delete_class(get_resource_obj):
    del_res = Delete(get_resource_obj)
    assert del_res.run_delete() is True


def test_update_class_nacl_rules(get_resource_obj):
    update_res = Update(get_resource_obj)
    assert update_res.update_nacl_rules() is True


def test_update_sg_rules(get_resource_obj, mocker, egress_rule, ssm_client):
    def mock_get_sg_rules(*args, **kwargs):
        return egress_rule

    mocker.patch('delete_aws_resources_with_py.main.Update.get_sg_rules', mock_get_sg_rules)

    def mock_revoke_sg_rule(*args, **kwargs):
        return {'Return': True}

    mocker.patch('delete_aws_resources_with_py.main.Update.revoke_ingress_sg_rule', mock_revoke_sg_rule)
    mocker.patch('delete_aws_resources_with_py.main.Update.revoke_egress_sg_rule', mock_revoke_sg_rule)
    print(get_resource_obj.sgs)

    actual = execute_changes_on_resources('modify', get_resource_obj, ssm_client, 'us-east-1')
    assert actual is True

# def test_update_class_sg_rules(get_resource_obj, mocker, egress_rule):
#     update_res = Update(get_resource_obj)
#     mocker.patch.object(
#         update_res,
#         'get_sg_rules',
#         return_value=egress_rule
#     )
#     mocker.patch.object(
#         update_res,
#         'update_sg_rules',
#         return_value=True
#     )
#     assert update_res.run_update() is True
#     assert update_res.update_sg_rules() is True
