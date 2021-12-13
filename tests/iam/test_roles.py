import pytest
import re
import six

from proknow import Exceptions

def test_create(app, role_generator):
    pk = app.pk

    # Verify returned RoleItem
    params, role = role_generator()
    assert role.name == params["name"]
    permissions = dict(params["permissions"])
    permissions["user"] = None
    permissions["private"] = False
    assert role.permissions == permissions

    # Assert item can be found in query
    for role in pk.roles.query():
        if role.name == params["name"]:
            role_match = role
            break
    else:
        role_match = None
    assert role_match is not None
    role = role_match.get()
    assert isinstance(role.data["id"], six.string_types)
    assert role.name == params["name"]
    assert role.permissions == permissions

def test_create_failure(app):
    pk = app.pk

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.roles.create("Admin", {
            "create_api_keys": False,
            "manage_access": False,
            "manage_custom_metrics": False,
            "manage_template_metric_sets": False,
            "manage_renaming_rules": False,
            "manage_template_checklists": False,
            "organization_collaborator": False,
            "organization_read_patients": False,
            "organization_read_collections": False,
            "organization_view_phi": False,
            "organization_download_dicom": False,
            "organization_upload_dicom": False,
            "organization_write_collections": False,
            "organization_write_patients": False,
            "organization_contour_patients": False,
            "organization_delete_collections": False,
            "organization_delete_patients": False,
            "workspaces": [],
        })
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Role already exists with name "Admin"'

def test_delete(app, role_generator):
    pk = app.pk

    params, role = role_generator(do_not_mark=True)

    # Verify role was deleted successfully
    role.delete()
    for role in pk.roles.query():
        if role.name == params["name"]:
            match = role
            break
    else:
        match = None
    assert match is None

def test_delete_failure(app, role_generator):
    pk = app.pk

    _, role = role_generator()

    # Assert error is raised when attempting to delete role that does not exist
    role.delete()
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        role.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == ('Role "' + role.id + '" not found')

def test_find(app, role_generator):
    pk = app.pk

    params, role = role_generator(name="Find Me")
    expr = re.compile(r"ind")

    # Find with no args
    found = pk.roles.find()
    assert found is None

    # Find using predicate
    found = pk.roles.find(lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is not None
    assert found.name == params["name"]

    # Find using props
    found = pk.roles.find(id=role.id, name=params["name"])
    assert found is not None
    assert found.name == params["name"]

    # Find using both
    found = pk.roles.find(lambda ws: expr.search(ws.data["name"]) is not None, id=role.id, name=params["name"])
    assert found is not None
    assert found.name == params["name"]

    # Find failure
    found = pk.roles.find(lambda ws: expr.search(ws.data["id"]) is not None)
    assert found is None
    found = pk.roles.find(id=role.id, name=params["name"].lower())
    assert found is None

def test_query(app, role_generator):
    pk = app.pk

    params1, _ = role_generator()
    params2, _ = role_generator()

    # Verify test 1
    for role in pk.roles.query():
        if role.name == params1["name"]:
            match = role
            break
    else:
        match = None
    assert match is not None

    # Verify test 2
    for role in pk.roles.query():
        if role.name == params2["name"]:
            match = role
            break
    else:
        match = None
    assert match is not None

def test_update(app, role_generator):
    pk = app.pk
    resource_prefix = app.resource_prefix

    params, role = role_generator()

    # Verify role was updated successfully
    updated_name = resource_prefix + "Updated Role Name"
    role.name = updated_name
    role.permissions["organization_read_patients"] = True
    role.save()
    for role in pk.roles.query():
        if role.name == updated_name:
            role_match = role
            break
    else:
        role_match = None
    assert role_match is not None
    role = role_match.get()
    assert isinstance(role.data["id"], six.string_types)
    assert role.name == updated_name
    assert role.permissions == {
        "create_api_keys": False,
        "manage_access": False,
        "manage_custom_metrics": False,
        "manage_template_metric_sets": False,
        "manage_renaming_rules": False,
        "manage_template_checklists": False,
        "manage_audit_logs": False,
        "manage_template_structure_sets": False,
        "manage_workspace_algorithms": False,
        "organization_manage_access_patients": False,
        "organization_collaborator": False,
        "organization_read_patients": True,
        "organization_read_collections": False,
        "organization_view_phi": False,
        "organization_download_dicom": False,
        "organization_upload_dicom": False,
        "organization_write_collections": False,
        "organization_write_patients": False,
        "organization_contour_patients": False,
        "organization_delete_collections": False,
        "organization_delete_patients": False,
        "workspaces": [],
        "private": False,
        "user": None,
    }

def test_update_failure(app, role_generator):
    pk = app.pk

    _, role = role_generator()

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        role.name = "Admin"
        role.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Role already exists with name "Admin"'
