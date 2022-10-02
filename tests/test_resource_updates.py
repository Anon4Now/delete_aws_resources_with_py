"""Module containing tests for Delete and Update classes"""

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


def test_update_class_sg_rules(get_resource_obj, mocker, egress_rule):
    update_res = Update(get_resource_obj)
    mocker.patch.object(
        update_res,
        'get_sg_rules',
        return_value=egress_rule
    )
    mocker.patch.object(
        update_res,
        'update_sg_rules',
        return_value=True
    )
    assert update_res.run_update() is True
    assert update_res.update_sg_rules() is True
