import pytest
import re
import six

from proknow import Exceptions

def test_create(app, role_generator):
    pk = app.pk

    # Verify returned RoleItem
    params, role = role_generator()
    assert role.name == params["name"]
    assert role.description == params["description"]
    permissions = dict(params["permissions"])
    for key, value in permissions.items():
        assert role.permissions[key] == value

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
    assert role.description == params["description"]
    for key, value in permissions.items():
        assert role.permissions[key] == value

def test_create_failure(app):
    pk = app.pk

    # Assert error is raised for duplicate roles
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.roles.create("User", "", {
            "workspaces_read": True
        })
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == '{"type":"ROLE_CONFLICT_NAME","params":{"name":"User"},"message":"Role already exists with name \\"User\\""}'

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
    assert err_wrapper.value.body == '{"type":"ROLE_NOT_FOUND","params":{"role_id":"' + role.id + '"},"message":"Role \\"' + role.id + '\\" not found"}'

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
        assert isinstance(role.id, six.string_types)
        if role.name == params1["name"] and role.description == params1["description"]:
            match = role
            break
    else:
        match = None
    assert match is not None

    # Verify test 2
    for role in pk.roles.query():
        assert isinstance(role.id, six.string_types)
        if role.name == params2["name"] and role.description == params2["description"]:
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
    role.permissions["collections_read"] = True
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
        'roles_read': True,
        'users_read': True,
        'groups_read': True,
        'patients_phi': False,
        'roles_create': False,
        'roles_delete': False,
        'roles_update': False,
        'users_create': False,
        'users_delete': False,
        'users_update': False,
        'groups_create': False,
        'groups_delete': False,
        'groups_update': False,
        'patients_copy': False,
        'patients_move': False,
        'patients_read': False,
        'workflows_read': True,
        'api_keys_create': True,
        'patients_create': False,
        'patients_delete': False,
        'patients_update': False,
        'workspaces_read': False,
        'collections_read': True,
        'patients_contour': False,
        'workflows_create': False,
        'workflows_delete': False,
        'workflows_update': False,
        'audit_logs_manage': False,
        'group_members_add': False,
        'workspaces_create': False,
        'workspaces_delete': False,
        'workspaces_update': False,
        'collections_create': False,
        'collections_delete': False,
        'collections_update': False,
        'group_members_list': True,
        'patient_notes_read': False,
        'custom_metrics_read': True,
        'renaming_rules_read': True,
        'group_members_remove': False,
        'patient_dicom_upload': False,
        'patient_notes_create': False,
        'patient_notes_delete': False,
        'patient_notes_update': False,
        'custom_metrics_create': False,
        'custom_metrics_delete': False,
        'custom_metrics_update': False,
        'renaming_rules_search': False,
        'renaming_rules_update': False,
        'patient_dicom_download': False,
        'patient_documents_read': False,
        'renaming_rules_execute': False,
        'collection_patients_add': False,
        'patient_checklists_read': False,
        'patient_scorecards_read': False,
        'checklist_templates_read': True,
        'objective_templates_read': True,
        'organizations_update': False,
        'patient_documents_create': False,
        'patient_documents_delete': False,
        'patient_documents_update': False,
        'resource_assignments_add': False,
        'scorecard_templates_read': True,
        'collection_bookmarks_read': False,
        'patient_checklists_create': False,
        'patient_checklists_delete': False,
        'patient_checklists_update': False,
        'patient_scorecards_create': False,
        'patient_scorecards_delete': False,
        'patient_scorecards_update': False,
        'resource_assignments_list': False,
        'workspace_algorithms_read': True,
        'checklist_templates_create': False,
        'checklist_templates_delete': False,
        'checklist_templates_update': False,
        'collection_patients_remove': False,
        'collection_scorecards_read': False,
        'objective_templates_create': False,
        'objective_templates_delete': False,
        'scorecard_templates_create': False,
        'scorecard_templates_delete': False,
        'scorecard_templates_update': False,
        'collection_bookmarks_create': False,
        'collection_bookmarks_delete': False,
        'collection_bookmarks_update': False,
        'resource_assignments_remove': False,
        'workspace_algorithms_update': False,
        'collection_scorecards_create': False,
        'collection_scorecards_delete': False,
        'collection_scorecards_update': False,
        'resource_permissions_resolve': True,
        'structure_set_templates_read': True,
        'structure_set_templates_create': False,
        'structure_set_templates_delete': False,
        'structure_set_templates_update': False
    }

def test_update_failure(app, role_generator):
    pk = app.pk

    _, role = role_generator()

    # Assert error is raised for duplicate role
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        role.name = "Owner"
        role.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == '{"type":"ROLE_CONFLICT_NAME","params":{"name":"Owner"},"message":"Role already exists with name \\"Owner\\""}'

    # Assert error is raised for system role
    system_role = pk.roles.find(name='Owner').get()
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        system_role.description = "New description"
        system_role.permissions["collections_read"] = True
        system_role.save()
    assert err_wrapper.value.status_code == 400
    assert err_wrapper.value.body == '{"type":"CANNOT_UPDATE_SYSTEM_ROLE","params":{},"message":"Invalid request to update system role"}'

    # Assert error is raised for constant permission
    system_role = pk.roles.find(name='Owner').get()
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        system_role.description = "New description"
        system_role.permissions["users_read"] = False
        system_role.save()
    assert err_wrapper.value.status_code == 422
    assert err_wrapper.value.body == '{"type":"VALIDATION_ERROR","params":{},"message":"child \'permissions.users_read\' must be equal to constant"}'    
