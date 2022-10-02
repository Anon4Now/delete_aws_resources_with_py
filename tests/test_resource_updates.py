"""Module containing tests for Delete and Update classes"""

# Local App imports
from delete_aws_resources_with_py.resource_updates import (
    Delete,
    Update
)


def test_delete_class(get_resource_obj):
    del_res = Delete(get_resource_obj)
    assert del_res.run_delete() is True
