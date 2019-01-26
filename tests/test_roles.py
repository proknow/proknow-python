import pytest
import re

from proknow import Exceptions

def test_create_roles(app):
    pk = app.pk

    # Verify returned RoleItem
    role = pk.roles.create("Create Test", {
        "create_api_keys": False,
        "manage_access": False,
        "manage_custom_metrics": False,
        "manage_template_metric_sets": False,
        "manage_renaming_rules": False,
        "manage_template_checklists": False,
        "organization_read": False,
        "organization_view_phi": False,
        "organization_download_dicom": False,
        "organization_write_collections": False,
        "organization_write_patients": False,
        "organization_contour_patients": False,
        "organization_delete_collections": False,
        "organization_delete_patients": False,
        "workspaces": [],
    })
    app.marked_roles.append(role) # mark for removal
    assert role.name == "Create Test"
    assert role.permissions == {
        "create_api_keys": False,
        "manage_access": False,
        "manage_custom_metrics": False,
        "manage_template_metric_sets": False,
        "manage_renaming_rules": False,
        "manage_template_checklists": False,
        "organization_read": False,
        "organization_view_phi": False,
        "organization_download_dicom": False,
        "organization_write_collections": False,
        "organization_write_patients": False,
        "organization_contour_patients": False,
        "organization_delete_collections": False,
        "organization_delete_patients": False,
        "workspaces": [],
    }

    # Assert item can be found in query
    for role in pk.roles.query():
        if role.name == "Create Test":
            role_match = role
            break
    else:
        role_match = None
    assert role_match is not None
    role = role_match.get()
    assert role.name == "Create Test"
    assert role.permissions == {
        "create_api_keys": False,
        "manage_access": False,
        "manage_custom_metrics": False,
        "manage_template_metric_sets": False,
        "manage_renaming_rules": False,
        "manage_template_checklists": False,
        "organization_read": False,
        "organization_view_phi": False,
        "organization_download_dicom": False,
        "organization_write_collections": False,
        "organization_write_patients": False,
        "organization_contour_patients": False,
        "organization_delete_collections": False,
        "organization_delete_patients": False,
        "workspaces": [],
    }

def test_create_roles_failure(app):
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
            "organization_read": False,
            "organization_view_phi": False,
            "organization_download_dicom": False,
            "organization_write_collections": False,
            "organization_write_patients": False,
            "organization_contour_patients": False,
            "organization_delete_collections": False,
            "organization_delete_patients": False,
            "workspaces": [],
        })
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Role already exists with name "Admin"'

def test_delete_roles(app, role_factory):
    pk = app.pk

    role = role_factory(("deleteme", {
        "create_api_keys": False,
        "manage_access": False,
        "manage_custom_metrics": False,
        "manage_template_metric_sets": False,
        "manage_renaming_rules": False,
        "manage_template_checklists": False,
        "organization_read": False,
        "organization_view_phi": False,
        "organization_download_dicom": False,
        "organization_write_collections": False,
        "organization_write_patients": False,
        "organization_contour_patients": False,
        "organization_delete_collections": False,
        "organization_delete_patients": False,
        "workspaces": [],
    }), do_not_mark=True)[0]

    # Verify role was deleted successfully
    role.delete()
    for role in pk.roles.query():
        if role.name == "deleteme":
            match = role
            break
    else:
        match = None
    assert match is None

def test_delete_roles_failure(app, role_factory):
    pk = app.pk

    role = pk.roles.find(name="Admin").get()

    # Assert error is raised when attempting to delete role that does not exist
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        role.delete()
    assert err_wrapper.value.status_code == 400
    assert err_wrapper.value.body == ('Role "' + role.id + '" is referenced by one or more users')

def test_find_roles(app, role_factory):
    pk = app.pk

    role = role_factory(("Find Me", {
        "create_api_keys": False,
        "manage_access": False,
        "manage_custom_metrics": False,
        "manage_template_metric_sets": False,
        "manage_renaming_rules": False,
        "manage_template_checklists": False,
        "organization_read": False,
        "organization_view_phi": False,
        "organization_download_dicom": False,
        "organization_write_collections": False,
        "organization_write_patients": False,
        "organization_contour_patients": False,
        "organization_delete_collections": False,
        "organization_delete_patients": False,
        "workspaces": [],
    }))[0]
    expr = re.compile(r"ind")

    # Find using predicate
    found = pk.roles.find(lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is not None
    assert found.name == "Find Me"

    # Find using props
    found = pk.roles.find(id=role.id, name="Find Me")
    assert found is not None
    assert found.name == "Find Me"

    # Find using both
    found = pk.roles.find(lambda ws: expr.search(ws.data["name"]) is not None, id=role.id, name="Find Me")
    assert found is not None
    assert found.name == "Find Me"

    # Find failure
    found = pk.roles.find(lambda ws: expr.search(ws.data["id"]) is not None)
    assert found is None
    found = pk.roles.find(id=role.id, name="Find me")
    assert found is None

def test_query_roles(app, role_factory):
    pk = app.pk

    role_factory([
        ("Test 1", {
            "create_api_keys": False,
            "manage_access": False,
            "manage_custom_metrics": False,
            "manage_template_metric_sets": False,
            "manage_renaming_rules": False,
            "manage_template_checklists": False,
            "organization_read": False,
            "organization_view_phi": False,
            "organization_download_dicom": False,
            "organization_write_collections": False,
            "organization_write_patients": False,
            "organization_contour_patients": False,
            "organization_delete_collections": False,
            "organization_delete_patients": False,
            "workspaces": [],
        }),
        ("Test 2", {
            "create_api_keys": False,
            "manage_access": False,
            "manage_custom_metrics": False,
            "manage_template_metric_sets": False,
            "manage_renaming_rules": False,
            "manage_template_checklists": False,
            "organization_read": False,
            "organization_view_phi": False,
            "organization_download_dicom": False,
            "organization_write_collections": False,
            "organization_write_patients": False,
            "organization_contour_patients": False,
            "organization_delete_collections": False,
            "organization_delete_patients": False,
            "workspaces": [],
        }),
    ])

    # Verify test 1
    for role in pk.roles.query():
        if role.name == "Test 1":
            match = role
            break
    else:
        match = None
    assert match is not None

    # Verify test 2
    for role in pk.roles.query():
        if role.name == "Test 2":
            match = role
            break
    else:
        match = None
    assert match is not None

def test_update_roles(app, role_factory):
    pk = app.pk

    role = role_factory([("updateme", {
        "create_api_keys": False,
        "manage_access": False,
        "manage_custom_metrics": False,
        "manage_template_metric_sets": False,
        "manage_renaming_rules": False,
        "manage_template_checklists": False,
        "organization_read": False,
        "organization_view_phi": False,
        "organization_download_dicom": False,
        "organization_write_collections": False,
        "organization_write_patients": False,
        "organization_contour_patients": False,
        "organization_delete_collections": False,
        "organization_delete_patients": False,
        "workspaces": [],
    })])[0]

    # Verify role was updated successfully
    role.name = "Updated Role Name"
    role.permissions["organization_read"] = True
    role.save()
    for role in pk.roles.query():
        if role.name == "Updated Role Name":
            role_match = role
            break
    else:
        role_match = None
    assert role_match is not None
    role = role_match.get()
    assert role.name == "Updated Role Name"
    assert role.permissions == {
        "create_api_keys": False,
        "manage_access": False,
        "manage_custom_metrics": False,
        "manage_template_metric_sets": False,
        "manage_renaming_rules": False,
        "manage_template_checklists": False,
        "organization_read": True,
        "organization_view_phi": False,
        "organization_download_dicom": False,
        "organization_write_collections": False,
        "organization_write_patients": False,
        "organization_contour_patients": False,
        "organization_delete_collections": False,
        "organization_delete_patients": False,
        "workspaces": [],
    }

def test_update_roles_failure(app, role_factory):
    pk = app.pk

    role = role_factory(("Update Me Failure", {
        "create_api_keys": False,
        "manage_access": False,
        "manage_custom_metrics": False,
        "manage_template_metric_sets": False,
        "manage_renaming_rules": False,
        "manage_template_checklists": False,
        "organization_read": False,
        "organization_view_phi": False,
        "organization_download_dicom": False,
        "organization_write_collections": False,
        "organization_write_patients": False,
        "organization_contour_patients": False,
        "organization_delete_collections": False,
        "organization_delete_patients": False,
        "workspaces": [],
    }))[0]

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        role.name = "Admin"
        role.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Role already exists with name "Admin"'
