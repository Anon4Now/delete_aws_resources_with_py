"""Module containing tests for Delete class"""

# Local App imports
from delete_aws_resources_with_py.resource_delete import Delete


def test_delete_class(get_resource_obj):
    del_res = Delete(get_resource_obj)
    assert del_res.delete_resources() is True
