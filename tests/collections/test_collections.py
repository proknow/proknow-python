import pytest
import re

from proknow import Exceptions

def test_create_collections(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    # Verify returned PatientItem for organization collection
    collection = pk.collections.create("Create Organization Collection 1", "Test Desc", "organization", [])
    app.marked_collections.append(collection)
    assert collection.name == "Create Organization Collection 1"
    assert collection.description == "Test Desc"

    # Assert item can be found in query
    collections = pk.collections.query()
    for collection in collections:
        if collection.name == "Create Organization Collection 1":
            collection_match = collection
            break
    else:
        collection_match = None
    assert collection_match is not None
    assert collection_match.name == "Create Organization Collection 1"
    assert collection_match.description == "Test Desc"

    # Verify returned PatientItem for workspace collection
    collection = pk.collections.create("Create Workspace Collection 1", "", "workspace", [workspace.id])
    app.marked_collections.append(collection)
    assert collection.name == "Create Workspace Collection 1"
    assert collection.description == ""

    # Assert item can be found in query
    collections = pk.collections.query(workspace.id)
    for collection in collections:
        if collection.name == "Create Workspace Collection 1":
            collection_match = collection
            break
    else:
        collection_match = None
    assert collection_match is not None
    assert collection_match.name == "Create Workspace Collection 1"
    assert collection_match.description == ""

def test_create_collections_failure(app, collection_generator):
    pk = app.pk

    params, _ = collection_generator()

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.collections.create(**params)
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Collection already exists with name "' + params["name"] + '"'

def test_delete_collections(app, collection_generator):
    pk = app.pk

    params, collection = collection_generator(do_not_mark=True)

    # Verify collection was deleted successfully
    collection.delete()
    for collection in pk.collections.query():
        if collection.name == params["name"]:
            match = collection
            break
    else:
        match = None
    assert match is None

def test_delete_collections_failure(app, collection_generator):
    pk = app.pk

    params, collection = collection_generator(do_not_mark=True)

    collection.delete()

    # Assert error is raised when attempting to delete collection that does not exist
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        collection.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'Collection "' + collection.id + '" not found'

def test_find_collections(app, collection_generator):
    pk = app.pk

    params, collection = collection_generator(name="Find Me")
    expr = re.compile(r"ind")

    # Find with no args
    found = pk.collections.find()
    assert found is None

    # Find using predicate
    found = pk.collections.find(predicate=lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is not None
    assert found.name == params["name"]
    assert found.description == params["description"]

    # Find using props
    found = pk.collections.find(id=collection.id, name=params["name"])
    assert found is not None
    assert found.name == params["name"]
    assert found.description == params["description"]

    # Find using both
    found = pk.collections.find(predicate=lambda ws: expr.search(ws.data["name"]) is not None, id=collection.id, name=params["name"])
    assert found is not None
    assert found.name == params["name"]
    assert found.description == params["description"]

    # Find failure
    found = pk.collections.find(predicate=lambda ws: expr.search(ws.data["id"]) is not None)
    assert found is None
    found = pk.collections.find(id=collection.id, name=params["name"].lower())
    assert found is None

def test_get_collections(app, workspace_generator, collection_generator):
    pk = app.pk

    _, workspace = workspace_generator()
    params, collection = collection_generator(type="workspace", workspaces=[workspace.id])

    found = pk.collections.find(workspace=workspace.id, id=collection.id)
    item = found.get()
    assert item.name == params["name"]
    assert item.description == params["description"]

def test_query_collections(app, workspace_generator, collection_generator):
    pk = app.pk

    params1, collection1 = collection_generator()
    params2, collection2 = collection_generator()

    # Verify test 1
    for collection in pk.collections.query():
        if collection.name == params1["name"]:
            match = collection
            break
    else:
        match = None
    assert match is not None
    assert match.id == collection1.id
    assert match.name == params1["name"]
    assert match.description == params1["description"]

    # Verify test 2
    for collection in pk.collections.query():
        if collection.name == params2["name"]:
            match = collection
            break
    else:
        match = None
    assert match is not None
    assert match.id == collection2.id
    assert match.name == params2["name"]
    assert match.description == params2["description"]

    _, workspace = workspace_generator()
    params3, collection3 = collection_generator(type="workspace", workspaces=[workspace.id])
    params4, collection4 = collection_generator(type="workspace", workspaces=[workspace.id])

    # Verify test 3
    for collection in pk.collections.query(workspace.id):
        if collection.name == params3["name"]:
            match = collection
            break
    else:
        match = None
    assert match is not None
    assert match.id == collection3.id
    assert match.name == params3["name"]
    assert match.description == params3["description"]

    # Verify test 3
    for collection in pk.collections.query(workspace.id):
        if collection.name == params4["name"]:
            match = collection
            break
    else:
        match = None
    assert match is not None
    assert match.id == collection4.id
    assert match.name == params4["name"]
    assert match.description == params4["description"]

def test_update_collections(app, collection_generator):
    pk = app.pk
    resource_prefix = app.resource_prefix

    params, collection = collection_generator()

    # Verify collection was updated successfully
    updated_name = resource_prefix + "Updated Collection Name"
    collection.name = updated_name
    collection.description = "Updated Collection Description"
    collection.save()
    for collection in pk.collections.query():
        if collection.name == updated_name:
            collection_match = collection
            break
    else:
        collection_match = None
    assert collection_match is not None
    collection = collection_match.get()
    assert collection.name == updated_name
    assert collection.description == "Updated Collection Description"

def test_update_collections_failure(app, collection_generator):
    pk = app.pk

    params, _ = collection_generator()
    _, collection = collection_generator()

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        collection.name = params["name"]
        collection.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Collection already exists with name "' + params["name"] + '"'
