import pytest
import os

from proknow import Exceptions

def test_collection_patients(app, workspace_generator, collection_generator):
    pk = app.pk

    _, workspace = workspace_generator()
    batch = pk.uploads.upload(workspace.id, "./data/Becker^Matthew")
    path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    patient_summary = batch.find_patient(path)
    entity_summary = batch.find_entity(path)

    # Create workspace collection
    _, collection = collection_generator(type="workspace", workspaces=[workspace.id])

    # Verify collection is empty
    patients = collection.patients.query()
    assert len(patients) == 0

    # Verify patient added to the collection
    collection.patients.add(workspace.id, [{
        "patient": patient_summary.id,
        "entity": entity_summary.id,
    }])
    patients = collection.patients.query()
    assert len(patients) == 1
    patient = patients[0]
    assert patient.id == patient_summary.id
    assert patient.entity_id == entity_summary.id
    assert isinstance(patient.data, dict)

    # Verify patient is removed from collection
    collection.patients.remove(workspace.id, [{
        "patient": patient_summary.id
    }])
    patients = collection.patients.query()
    assert len(patients) == 0

    # Verify patient without representative entity is added to the collection
    collection.patients.add(workspace.id, [{
        "patient": patient_summary.id
    }])
    patients = collection.patients.query()
    assert len(patients) == 1
    patient = patients[0]
    assert patient.id == patient_summary.id
    assert patient.entity_id is None
    assert isinstance(patient.data, dict)

    # Verify patient is removed from collection
    collection.patients.remove(workspace.id, [{
        "patient": patient_summary.id
    }])
    patients = collection.patients.query()
    assert len(patients) == 0

    # Create organization collection
    _, collection = collection_generator(workspaces=[workspace.id])

    # Verify collection is empty
    patients = collection.patients.query()
    assert len(patients) == 0

    # Verify patient added to the collection
    collection.patients.add(workspace.id, [{
        "patient": patient_summary.id,
        "entity": entity_summary.id,
    }])
    patients = collection.patients.query()
    assert len(patients) == 1
    patient = patients[0]
    assert patient.id == patient_summary.id
    assert patient.entity_id == entity_summary.id
    assert isinstance(patient.data, dict)

    # Verify patient is removed from collection
    collection.patients.remove(workspace.id, [{
        "patient": patient_summary.id
    }])
    patients = collection.patients.query()
    assert len(patients) == 0

    # Verify patient without representative entity is added to the collection
    collection.patients.add(workspace.id, [{
        "patient": patient_summary.id
    }])
    patients = collection.patients.query()
    assert len(patients) == 1
    patient = patients[0]
    assert patient.id == patient_summary.id
    assert patient.entity_id is None
    assert isinstance(patient.data, dict)

    # Verify patient is removed from collection
    collection.patients.remove(workspace.id, [{
        "patient": patient_summary.id
    }])
    patients = collection.patients.query()
    assert len(patients) == 0

def test_collection_patients_failure(app, workspace_generator, collection_generator):
    pk = app.pk

    _, workspace = workspace_generator()
    _, collection = collection_generator(workspaces=[workspace.id])
    batch = pk.uploads.upload(workspace.id, "./data/Becker^Matthew")
    path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
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

def test_collection_patients_get(app, workspace_generator, collection_generator):
    pk = app.pk

    _, workspace = workspace_generator()
    _, collection = collection_generator(workspaces=[workspace.id])
    batch = pk.uploads.upload(workspace.id, "./data/Becker^Matthew")
    path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    patient_summary = batch.find_patient(path)
    entity_summary = batch.find_entity(path)
    collection.patients.add(workspace.id, [{
        "patient": patient_summary.id,
        "entity": entity_summary.id,
    }])

    # Verify correct patient information is returned
    patients = collection.patients.query()
    patient = patients[0].get()
    assert patient.id == patient_summary.id
    assert patient.mrn == patient_summary.data["mrn"]
    assert patient.name == patient_summary.data["name"]
