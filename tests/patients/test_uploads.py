import pytest
import re
import os
import six

from proknow import Exceptions

def test_upload(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    batch = pk.uploads.upload(workspace.id, "./tests/data/Becker^Matthew")
    assert len(batch.patients) == 1
    for patient_summary in batch.patients:
        assert len(patient_summary.entities) == 4

def test_upload_failure(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        pk.uploads.upload(workspace.id, "./path/to/nowhere")
    assert err_wrapper.value.message == "`./path/to/nowhere` is invalid."

    with pytest.raises(Exceptions.WorkspaceLookupError) as err_wrapper:
        pk.uploads.upload("Not a Workspace", "./tests/data/Becker^Matthew")
    assert err_wrapper.value.message == "Workspace with name `Not a Workspace` not found."

def test_upload_progress(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    def progress_updater(progress):
        if progress_updater.called == 0:
            progress_updater.first = dict(progress)
        progress_updater.progress = progress
        progress_updater.called += 1
    progress_updater.first = None
    progress_updater.progress = None
    progress_updater.called = 0

    pk.uploads.upload(workspace.id, "./tests/data/Becker^Matthew", progress_updater=progress_updater)
    assert progress_updater.called > 0
    assert progress_updater.progress is not None
    assert progress_updater.progress["total"] == 8
    assert progress_updater.progress["uploaded"] == 8
    assert progress_updater.progress["processed"] == 8
    assert progress_updater.first["total"] > progress_updater.first["uploaded"]
    assert progress_updater.first["total"] > progress_updater.first["processed"]

def test_upload_batch_find_patient(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    patient = batch.find_patient(path)
    assert patient == batch.patients[0]

def test_upload_batch_file_patient_failure(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        patient = batch.find_patient(path + "m")
    assert err_wrapper.value.message == '`' + path + 'm` not found in current batch'

def test_upload_batch_find_entity(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    image_set_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm")
    structure_set_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    plan_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    dose_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1_Dose.dcm")

    batch = pk.uploads.upload(workspace.id, "./tests/data/Becker^Matthew")
    entities = batch.patients[0].entities
    assert len(entities) == 4
    for entity in entities:
        if entity.data["type"] == "image_set":
            assert entity == batch.find_entity(image_set_path)
        elif entity.data["type"] == "structure_set":
            assert entity == batch.find_entity(structure_set_path)
        elif entity.data["type"] == "plan":
            assert entity == batch.find_entity(plan_path)
        elif entity.data["type"] == "dose":
            assert entity == batch.find_entity(dose_path)
        else:
            raise ValueError("Unexpected type: " + entity.data["type"])

def test_upload_batch_find_entity_failure(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        entity = batch.find_entity(path + "m")
    assert err_wrapper.value.message == '`' + path + 'm` not found in current batch'

def test_upload_patient_summary_get(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    patient_summary = batch.find_patient(path)
    patient_item = patient_summary.get()
    assert patient_item is not None
    assert isinstance(patient_item.data, dict)

def test_upload_entity_summary_get(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    entity_summary = batch.find_entity(path)
    entity_item = entity_summary.get()
    assert entity_item is not None
    assert isinstance(entity_item.data, dict)
