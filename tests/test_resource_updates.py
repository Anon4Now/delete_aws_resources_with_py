"""Module containing tests for Delete and Update classes"""

# Local App imports
from delete_aws_resources_with_py.resource_updates import (
    UpdateNaclResource,
    UpdateSgResource
)


def test_update_class_nacl_rules(get_resource_obj):
    update_res = UpdateNaclResource(get_resource_obj)
    assert update_res.update_nacl_rules() is True


def test_update_class_sg_rules(fake_resource_obj, fake_boto_client):
    fake_data = {'something': 'anything'}
    upd_sg = UpdateSgResource(fake_resource_obj)
    assert upd_sg.get_sg_rules('sg-04f64a24f0250f7e5') == 'sgr-0f5d697d6bde6f9da'
    assert upd_sg.revoke_egress_sg_rule(fake_data) is True
    assert upd_sg.revoke_ingress_sg_rule(fake_data) is True
