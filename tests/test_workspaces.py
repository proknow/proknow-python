import pytest
import re

from proknow import Exceptions

def test_create_workspaces(app):
    pk = app.pk

    # Verify returned WorkspaceItem
    workspace = pk.workspaces.create("create-test", "Create Test", False)
    app.marked_workspaces.append(workspace) # mark for removal
    assert workspace.slug == "create-test"
    assert workspace.name == "Create Test"
    assert workspace.protected == False

    # Assert item can be found in query
    workspaces = pk.workspaces.query()
    for workspace in workspaces:
        if workspace.slug == "create-test":
            workspace_match = workspace
            break
    else:
        workspace_match = None
    assert workspace_match is not None
    assert workspace_match.slug == "create-test"
    assert workspace_match.name == "Create Test"
    assert workspace_match.protected == False

def test_create_workspaces_failure(app):
    pk = app.pk

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.workspaces.create("clinical", "Clinical")
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Workspace already exists with slug "clinical"'

def test_delete_workspaces(app, workspace_factory):
    pk = app.pk

    workspace = workspace_factory(("deleteme", "Delete Me", False), do_not_mark=True)[0]

    # Verify workspace was deleted successfully
    workspace.delete()
    for workspace in pk.workspaces.query():
        if workspace.slug == "deleteme":
            match = workspace
            break
    else:
        match = None
    assert match is None

def test_delete_workspaces_failure(app, workspace_factory):
    pk = app.pk

    workspace = workspace_factory(("deleteme-failure", "Delete Me Failure", True))[0]

    # Assert error is raised when attempting to delete protected workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        workspace.delete()
    assert err_wrapper.value.status_code == 400
    assert err_wrapper.value.body == ('Workspace "' + workspace.id + '" is protected from '
        'accidental deletion. To delete the workspace, you must first turn off accidental '
        'deletion protection.')

def test_find_workspaces(app, workspace_factory):
    pk = app.pk

    workspace = workspace_factory(("findme", "Find Me"))[0]
    expr = re.compile(r"indm")

    # Find using predicate
    found = pk.workspaces.find(lambda ws: expr.search(ws.data["slug"]) is not None)
    assert found is not None
    assert found.slug == "findme"
    assert found.name == "Find Me"
    assert found.protected == True

    # Find using props
    found = pk.workspaces.find(slug="findme", name="Find Me")
    assert found is not None
    assert found.slug == "findme"
    assert found.name == "Find Me"
    assert found.protected == True

    # Find using both
    found = pk.workspaces.find(lambda ws: expr.search(ws.data["slug"]) is not None, slug="findme", name="Find Me")
    assert found is not None
    assert found.slug == "findme"
    assert found.name == "Find Me"
    assert found.protected == True

    # Find failure
    found = pk.workspaces.find(lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is None
    found = pk.workspaces.find(slug="findme", name="Find me")
    assert found is None

def test_query_workspaces(app, workspace_factory):
    pk = app.pk

    workspace_factory([
        ("test-1", "Test 1"),
        ("test-2", "Test 2", False),
    ])

    # Verify test 1
    for workspace in pk.workspaces.query():
        if workspace.slug == "test-1":
            match = workspace
            break
    else:
        match = None
    assert match is not None
    assert match.slug == "test-1"
    assert match.name == "Test 1"
    assert match.protected == True

    # Verify test 2
    for workspace in pk.workspaces.query():
        if workspace.slug == "test-2":
            match = workspace
            break
    else:
        match = None
    assert match is not None
    assert match.slug == "test-2"
    assert match.name == "Test 2"
    assert match.protected == False

def test_resolve(app, workspace_factory):
    pk = app.pk

    workspace = workspace_factory([("resolve-test-1", "Resolve Test 1")])[0]

    # Test resolve by id
    resolved = pk.workspaces.resolve(workspace.id)
    assert resolved is not None
    assert resolved.slug == "resolve-test-1"
    assert resolved.name == "Resolve Test 1"
    assert resolved.protected == True

    # Test resolve by name
    resolved = pk.workspaces.resolve("Resolve Test 1")
    assert resolved is not None
    assert resolved.slug == "resolve-test-1"
    assert resolved.name == "Resolve Test 1"
    assert resolved.protected == True

def test_resolve_failure(app):
    pk = app.pk

    # Test resolve by id
    with pytest.raises(Exceptions.WorkspaceLookupError) as err_wrapper:
        pk.workspaces.resolve("00000000000000000000000000000000")
    assert err_wrapper.value.message == "Workspace with id `00000000000000000000000000000000` not found."

    # Test resolve by name
    with pytest.raises(Exceptions.WorkspaceLookupError) as err_wrapper:
        pk.workspaces.resolve("My Workspace")
    assert err_wrapper.value.message == "Workspace with name `My Workspace` not found."

def test_resolve_by_id(app, workspace_factory):
    pk = app.pk

    workspace = workspace_factory([("resolve-by-id-test-1", "Resolve By Id Test 1")])[0]

    resolved = pk.workspaces.resolve_by_id(workspace.id)
    assert resolved is not None
    assert resolved.slug == "resolve-by-id-test-1"
    assert resolved.name == "Resolve By Id Test 1"
    assert resolved.protected == True

def test_resolve_by_id_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.WorkspaceLookupError) as err_wrapper:
        pk.workspaces.resolve_by_id("00000000000000000000000000000000")
    assert err_wrapper.value.message == "Workspace with id `00000000000000000000000000000000` not found."

def test_resolve_by_name(app, workspace_factory):
    pk = app.pk

    workspace = workspace_factory([("resolve-by-name-test-1", "Resolve By Name Test 1")])[0]

    resolved = pk.workspaces.resolve_by_name("Resolve By Name Test 1")
    assert resolved is not None
    assert resolved.slug == "resolve-by-name-test-1"
    assert resolved.name == "Resolve By Name Test 1"
    assert resolved.protected == True

def test_resolve_by_name_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.WorkspaceLookupError) as err_wrapper:
        pk.workspaces.resolve("My Workspace")
    assert err_wrapper.value.message == "Workspace with name `My Workspace` not found."

def test_update_workspaces(app, workspace_factory):
    pk = app.pk

    workspace = workspace_factory([("updateme", "Update Me")])[0]

    # Verify workspace was updated successfully
    workspace.slug = "updated"
    workspace.name = "Updated Workspace Name"
    workspace.protected = False
    workspace.save()
    workspaces = pk.workspaces.query()
    for workspace in workspaces:
        if workspace.slug == "updated":
            workspace_match = workspace
            break
    else:
        workspace_match = None
    assert workspace_match is not None
    assert workspace_match.slug == "updated"
    assert workspace_match.name == "Updated Workspace Name"
    assert workspace_match.protected == False

def test_update_workspaces_failure(app, workspace_factory):
    pk = app.pk

    workspace_factory(("updateme-failure", "Update Me Failure", True))

    # Assert error is raised for duplicate workspace
    workspace = pk.workspaces.find(slug="updateme-failure")
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        workspace.slug = "clinical"
        workspace.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Workspace already exists with slug "clinical"'
