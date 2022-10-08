"""Module containing tests for main module in script."""
import pytest

from delete_aws_resources_with_py.main import (
    main,
    execute_changes_on_resources,
    check_user_arg_response,
    get_region_list,
    create_boto_objects
)
from delete_aws_resources_with_py.errors import UserArgNotFoundError


def test_check_user_arg_response():
    with pytest.raises(UserArgNotFoundError):
        check_user_arg_response('hello')

    assert check_user_arg_response('delete') is True
    assert check_user_arg_response('modify') is True

