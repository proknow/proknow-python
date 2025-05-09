import pytest
import re

from proknow import Exceptions

def test_create(app, workspace_generator):
    pk = app.pk

    # Verify returned WorkspaceItem
    params, created = workspace_generator()
    assert created.slug == params["slug"]
    assert created.name == params["name"]
    assert created.protected == params["protected"]

    # Assert item can be found in query
    workspaces = pk.workspaces.query()
    for workspace in workspaces:
        if workspace.slug == params["slug"]:
            workspace_match = workspace
            break
    else:
        workspace_match = None
    assert workspace_match is not None
    assert workspace_match.slug == params["slug"]
    assert workspace_match.name == params["name"]
    assert workspace_match.protected == params["protected"]

def test_create_failure(app, workspace_generator):
    pk = app.pk

    params, _ = workspace_generator()

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.workspaces.create(**params)
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == '{"type":"WORKSPACE_CONFLICT_SLUG","params":{"slug":"' + params["slug"] + '"},"message":"Workspace already exists with slug \\"' + params["slug"] + '\\""}'

def test_delete(app, workspace_generator):
    pk = app.pk

    params, workspace = workspace_generator(do_not_mark=True)

    # Verify workspace was deleted successfully
    workspace.delete()
    for workspace in pk.workspaces.query():
        if workspace.slug == params["slug"]:
            match = workspace
            break
    else:
        match = None
    assert match is None

def test_delete_failure(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator(do_not_mark=True)

    workspace.delete()

    # Assert error is raised when attempting to delete protected workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        workspace.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == '{"type":"WORKSPACE_NOT_FOUND","params":{"workspace_id":"' + workspace.id + '"},"message":"Workspace \\"' + workspace.id + '\\" not found"}'

def test_find(app, workspace_generator):
    pk = app.pk

    params, _ = workspace_generator(slug="findme", name="Find Me")
    expr = re.compile(r"indm")

    # Find with no args
    found = pk.workspaces.find()
    assert found is None

    # Find using predicate
    found = pk.workspaces.find(lambda ws: expr.search(ws.data["slug"]) is not None)
    assert found is not None
    assert found.slug == params["slug"]
    assert found.name == params["name"]
    assert found.protected == params["protected"]

    # Find using props
    found = pk.workspaces.find(slug=params["slug"], name=params["name"])
    assert found is not None
    assert found.slug == params["slug"]
    assert found.name == params["name"]
    assert found.protected == params["protected"]

    # Find using both
    found = pk.workspaces.find(lambda ws: expr.search(ws.data["slug"]) is not None, slug=params["slug"], name=params["name"])
    assert found is not None
    assert found.slug == params["slug"]
    assert found.name == params["name"]
    assert found.protected == params["protected"]

    # Find failure
    found = pk.workspaces.find(lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is None
    found = pk.workspaces.find(slug="findme", name="Find me")
    assert found is None

def test_query(app, workspace_generator):
    pk = app.pk

    params1, _ = workspace_generator()
    params2, _ = workspace_generator()

    # Verify test 1
    for workspace in pk.workspaces.query():
        if workspace.slug == params1["slug"]:
            match = workspace
            break
    else:
        match = None
    assert match is not None
    assert match.slug == params1["slug"]
    assert match.name == params1["name"]
    assert match.protected == params1["protected"]

    # Verify test 2
    for workspace in pk.workspaces.query():
        if workspace.slug == params2["slug"]:
            match = workspace
            break
    else:
        match = None
    assert match is not None
    assert match.slug == params2["slug"]
    assert match.name == params2["name"]
    assert match.protected == params2["protected"]

def test_resolve(app, workspace_generator):
    pk = app.pk

    params, workspace = workspace_generator()

    # Test resolve by id
    resolved = pk.workspaces.resolve(workspace.id)
    assert resolved is not None
    assert resolved.slug == params["slug"]
    assert resolved.name == params["name"]
    assert resolved.protected == params["protected"]

    # Test resolve by name
    resolved = pk.workspaces.resolve(params["name"])
    assert resolved is not None
    assert resolved.slug == params["slug"]
    assert resolved.name == params["name"]
    assert resolved.protected == params["protected"]

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

def test_resolve_by_id(app, workspace_generator):
    pk = app.pk

    params, workspace = workspace_generator()

    resolved = pk.workspaces.resolve_by_id(workspace.id)
    assert resolved is not None
    assert resolved.slug == params["slug"]
    assert resolved.name == params["name"]
    assert resolved.protected == params["protected"]

def test_resolve_by_id_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.WorkspaceLookupError) as err_wrapper:
        pk.workspaces.resolve_by_id("00000000000000000000000000000000")
    assert err_wrapper.value.message == "Workspace with id `00000000000000000000000000000000` not found."

def test_resolve_by_name(app, workspace_generator):
    pk = app.pk

    params, workspace = workspace_generator(name="workspace-lower1")

    resolved = pk.workspaces.resolve_by_name(params["name"])
    assert resolved is not None
    assert resolved.slug == params["slug"]
    assert resolved.name == params["name"]
    assert resolved.protected == params["protected"]

    resolved = pk.workspaces.resolve_by_name(params["name"].upper())
    assert resolved is not None
    assert resolved.slug == params["slug"]
    assert resolved.name == params["name"]
    assert resolved.protected == params["protected"]

def test_resolve_by_name_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.WorkspaceLookupError) as err_wrapper:
        pk.workspaces.resolve("My Workspace")
    assert err_wrapper.value.message == "Workspace with name `My Workspace` not found."

def test_update(app, workspace_generator):
    pk = app.pk
    resource_prefix = app.resource_prefix

    params, workspace = workspace_generator()

    # Verify workspace was updated successfully
    workspace.slug = resource_prefix + "updated"
    workspace.name = "Updated Workspace Name"
    workspace.protected = True
    workspace.save()
    workspaces = pk.workspaces.query()
    for workspace in workspaces:
        if workspace.slug == resource_prefix + "updated":
            workspace_match = workspace
            break
    else:
        workspace_match = None
    assert workspace_match is not None
    assert workspace_match.slug == resource_prefix + "updated"
    assert workspace_match.name == "Updated Workspace Name"
    assert workspace_match.protected == True

def test_update_failure(app, workspace_generator):
    pk = app.pk

    params, _ = workspace_generator()
    _, workspace = workspace_generator()

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        workspace.slug = params["slug"]
        workspace.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == '{"type":"WORKSPACE_CONFLICT_SLUG","params":{"slug":"' + params["slug"] + '"},"message":"Workspace already exists with slug \\"' + params["slug"] + '\\""}'

def test_update_entities(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()
    patient = pk.patients.create(workspace.id, "1000", "Last^First", "2018-01-01", "M")

    patient.upload([
        "./data/Jensen^Myrtle/HNC0522c0013_CT1_image00000.dcm",
        "./data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm",
    ])
    patient.refresh()
    image_sets = [entity.get() for entity in patient.find_entities(type="image_set")]
    assert len(image_sets) == 2
    assert image_sets[0].data["frame_of_reference"] != image_sets[1].data["frame_of_reference"]
    workspace.update_entities({
        "frame_of_reference": image_sets[0].data["frame_of_reference"]
    }, [image_sets[0], image_sets[1].id])
    for image_set in image_sets:
        image_set.refresh()
    assert image_sets[0].data["frame_of_reference"] == image_sets[1].data["frame_of_reference"]

def test_update_entities_failure(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()
    patient = pk.patients.create(workspace.id, "1000", "Last^First", "2018-01-01", "M")

    # Assert error is raised for invalid entity ids
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        workspace.update_entities({
            "frame_of_reference": "1.3.6.1.4.1.22213.2.26558.1"
        }, ["00000000000000000000000000000000"])
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == '{"type":"ANY_ENTITY_NOT_FOUND","params":{},"message":"One or more entities not found"}'
