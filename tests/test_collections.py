import pytest
import re
import os

from proknow import Exceptions

def test_create_collections(app, workspace_factory):
    pk = app.pk

    workspace = workspace_factory(("create-collections-test", "Create Collections Test", False))[0]

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
    collections = pk.collections.query("Create Collections Test")
    for collection in collections:
        if collection.name == "Create Workspace Collection 1":
            collection_match = collection
            break
    else:
        collection_match = None
    assert collection_match is not None
    assert collection_match.name == "Create Workspace Collection 1"
    assert collection_match.description == ""

def test_create_collections_failure(app, collection_factory):
    pk = app.pk

    collection_factory(("Duplicate Me 1", "", "organization", []))

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.collections.create("Duplicate Me 1", "", "organization", [])
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Collection already exists with name "Duplicate Me 1"'


def test_delete_collections(app, collection_factory):
    pk = app.pk

    collection = collection_factory(("Delete Me", "", "organization", []), do_not_mark=True)[0]

    # Verify collection was deleted successfully
    collection.delete()
    for collection in pk.collections.query():
        if collection.name == "Delete Me":
            match = collection
            break
    else:
        match = None
    assert match is None

def test_delete_collections_failure(app, collection_factory):
    pk = app.pk

    collection = collection_factory(("Delete Me Failure", "", "organization", []), do_not_mark=True)[0]

    collection.delete()

    # Assert error is raised when attempting to delete collection that does not exist
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        collection.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'Collection "' + collection.id + '" not found.'

def test_find_collections(app, collection_factory):
    pk = app.pk

    collection = collection_factory(("Find Me", "", "organization", []))[0]
    expr = re.compile(r"ind")

    # Find using predicate
    found = pk.collections.find(predicate=lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is not None
    assert found.name == "Find Me"
    assert found.description == ""

    # Find using props
    found = pk.collections.find(id=collection.id, name="Find Me")
    assert found is not None
    assert found.name == "Find Me"
    assert found.description == ""

    # Find using both
    found = pk.collections.find(predicate=lambda ws: expr.search(ws.data["name"]) is not None, id=collection.id, name="Find Me")
    assert found is not None
    assert found.name == "Find Me"
    assert found.description == ""

    # Find failure
    found = pk.collections.find(predicate=lambda ws: expr.search(ws.data["id"]) is not None)
    assert found is None
    found = pk.collections.find(id=collection.id, name="Find me")
    assert found is None

def test_query_collections(app, workspace_factory, collection_factory):
    pk = app.pk

    result = collection_factory([
        ("Test Collection 1", "", "organization", []),
        ("Test Collection 2", "", "organization", []),
    ])

    # Verify test 1
    for collection in pk.collections.query():
        if collection.name == "Test Collection 1":
            match = collection
            break
    else:
        match = None
    assert match is not None
    assert match.id == result[0].id
    assert match.name == "Test Collection 1"
    assert match.description == ""

    # Verify test 2
    for collection in pk.collections.query():
        if collection.name == "Test Collection 2":
            match = collection
            break
    else:
        match = None
    assert match is not None
    assert match.id == result[1].id
    assert match.name == "Test Collection 2"
    assert match.description == ""

    workspace = workspace_factory(("query-collections-test", "Query Collections Test", False))[0]
    result = collection_factory([
        ("Test Collection 3", "", "workspace", [workspace.id]),
        ("Test Collection 4", "", "workspace", [workspace.id]),
    ])

    # Verify test 1
    for collection in pk.collections.query("Query Collections Test"):
        if collection.name == "Test Collection 3":
            match = collection
            break
    else:
        match = None
    assert match is not None
    assert match.id == result[0].id
    assert match.name == "Test Collection 3"
    assert match.description == ""

    # Verify test 2
    for collection in pk.collections.query("Query Collections Test"):
        if collection.name == "Test Collection 4":
            match = collection
            break
    else:
        match = None
    assert match is not None
    assert match.id == result[1].id
    assert match.name == "Test Collection 4"
    assert match.description == ""

def test_update_collections(app, collection_factory):
    pk = app.pk

    collection = collection_factory(("Update Me", "", "organization", []))[0]

    # Verify collection was updated successfully
    collection.name = "Updated Collection Name"
    collection.description = "Updated Collection Description"
    collection.save()
    for collection in pk.collections.query():
        if collection.name == "Updated Collection Name":
            collection_match = collection
            break
    else:
        collection_match = None
    assert collection_match is not None
    collection = collection_match.get()
    assert collection.name == "Updated Collection Name"
    assert collection.description == "Updated Collection Description"

def test_update_collections_failure(app, collection_factory):
    pk = app.pk

    collection = collection_factory([
        ("Update Me Failure", "", "organization", []),
        ("Duplicate Me 2", "", "organization", []),
    ])[0]

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        collection.name = "Duplicate Me 2"
        collection.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Collection already exists with name "Duplicate Me 2"'

def test_collection_patients(app, workspace_factory, collection_factory):
    pk = app.pk

    workspace = workspace_factory(("patients-test", "Patients Test", False))[0]
    batch = pk.uploads.upload("Patients Test", "./tests/data/Becker^Matthew")
    path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    patient_summary = batch.find_patient(path)
    entity_summary = batch.find_entity(path)

    # Create workspace collection
    collection = collection_factory(("Patients Test Collection", "", "workspace", [workspace.id]))[0]

    # Verify collection is empty
    patients = collection.patients.query()
    assert len(patients) == 0

    # Verify patient added to the collection
    collection.patients.add("Patients Test", [{
        "patient": patient_summary.id,
        "entity": entity_summary.id,
    }])
    patients = collection.patients.query()
    assert len(patients) == 1
    patient = patients[0]
    assert patient.id == patient_summary.id
    assert patient.entity_id == entity_summary.id

    # Verify patient is removed from collection
    collection.patients.remove("Patients Test", [{
        "patient": patient_summary.id
    }])
    patients = collection.patients.query()
    assert len(patients) == 0

    # Create organization collection
    collection = collection_factory(("Patients Test Collection", "", "organization", [workspace.id]))[0]

    # Verify collection is empty
    patients = collection.patients.query()
    assert len(patients) == 0

    # Verify patient added to the collection
    collection.patients.add("Patients Test", [{
        "patient": patient_summary.id,
        "entity": entity_summary.id,
    }])
    patients = collection.patients.query()
    assert len(patients) == 1
    patient = patients[0]
    assert patient.id == patient_summary.id
    assert patient.entity_id == entity_summary.id

    # Verify patient is removed from collection
    collection.patients.remove("Patients Test", [{
        "patient": patient_summary.id
    }])
    patients = collection.patients.query()
    assert len(patients) == 0

def test_collection_patients_failure(app, workspace_factory, collection_factory):
    pk = app.pk

    workspace = workspace_factory(("patients-failure-test", "Patients Failure Test", False))[0]
    collection = collection_factory(("Patients Failure Test Collection", "", "organization", [workspace.id]))[0]
    batch = pk.uploads.upload("Patients Failure Test", "./tests/data/Becker^Matthew")
    path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    patient_summary = batch.find_patient(path)
    entity_summary = batch.find_entity(path)

    # Assert exception is raised
    with pytest.raises(Exceptions.WorkspaceLookupError) as err_wrapper:
        collection.patients.add("Does Not Exist", [{
            "patient": patient_summary.id,
            "entity": entity_summary.id,
        }])
    assert err_wrapper.value.message == 'Workspace with name `Does Not Exist` not found.'

    # Assert exception is raised
    with pytest.raises(Exceptions.WorkspaceLookupError) as err_wrapper:
        collection.patients.remove("Does Not Exist", [{
            "patient": patient_summary.id,
        }])
    assert err_wrapper.value.message == 'Workspace with name `Does Not Exist` not found.'

def test_collection_patients_get(app, workspace_factory, collection_factory):
    pk = app.pk

    workspace = workspace_factory(("patients-get-test", "Patients Get Test", False))[0]
    collection = collection_factory(("Patients Get Test Collection", "", "organization", [workspace.id]))[0]
    batch = pk.uploads.upload("Patients Get Test", "./tests/data/Becker^Matthew")
    path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    patient_summary = batch.find_patient(path)
    entity_summary = batch.find_entity(path)
    collection.patients.add("Patients Get Test", [{
        "patient": patient_summary.id,
        "entity": entity_summary.id,
    }])

    # Verify correct patient information is returned
    patients = collection.patients.query()
    patient = patients[0].get()
    assert patient.id == patient_summary.id
    assert patient.mrn == patient_summary.data["mrn"]
    assert patient.name == patient_summary.data["name"]
