import pytest
import re
import os

from proknow import Exceptions

def test_upload(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    batch = pk.uploads.upload(workspace.id, "./data/Becker^Matthew")
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
        pk.uploads.upload("Not a Workspace", "./data/Becker^Matthew")
    assert err_wrapper.value.message == "Workspace with name `Not a Workspace` not found."

def test_upload_batch_find_patient(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    patient = batch.find_patient(path)
    assert patient == batch.patients[0]

def test_upload_batch_file_patient_failure(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        patient = batch.find_patient(path + "m")
    assert err_wrapper.value.message == '`' + path + 'm` not found in current batch'

def test_upload_batch_find_entity(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    image_set_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm")
    structure_set_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    plan_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    dose_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1_Dose.dcm")

    batch = pk.uploads.upload(workspace.id, "./data/Becker^Matthew")
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

    path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        entity = batch.find_entity(path + "m")
    assert err_wrapper.value.message == '`' + path + 'm` not found in current batch'

def test_upload_batch_find_sro(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    identity_path = os.path.abspath("./data/Registration/reg_identity.dcm")
    sro_path = os.path.abspath("./data/Registration/reg.dcm")
    no_imgs_path = os.path.abspath("./data/Registration/reg_no_imgs.dcm")

    batch = pk.uploads.upload(workspace.id, "./data/Registration")
    sros = batch.patients[0].sros
    assert len(sros) == 3
    for sro in sros:
        print(sro.data)
        if sro.data["uid"] == "1.2.826.0.1.3680043.8.498.28068777392206796577852532328666550263":
                assert sro == batch.find_sro(no_imgs_path)
        elif sro.data["uid"] == "1.2.246.352.221.52738008096457865345287404867971417273":
            assert sro == batch.find_sro(identity_path)
        elif sro.data["uid"] == "1.2.246.352.221.52738008096457865345287404867971417272":
            assert sro == batch.find_sro(sro_path)
        else:
            raise ValueError("Unexpected name: " + sro.data["name"])

def test_upload_batch_find_sro_failure(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./data/Registration/reg_identity.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        sro = batch.find_sro(path + "m")
    assert err_wrapper.value.message == '`' + path + 'm` not found in current batch'

def test_upload_patient_summary_get(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    patient_summary = batch.find_patient(path)
    patient_item = patient_summary.get()
    assert patient_item is not None
    assert isinstance(patient_item.data, dict)

def test_upload_entity_summary_get(app, workspace_generator):
    pk = app.pk

    _, workspace = workspace_generator()

    path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    batch = pk.uploads.upload(workspace.id, path)
    entity_summary = batch.find_entity(path)
    entity_item = entity_summary.get()
    assert entity_item is not None
    assert isinstance(entity_item.data, dict)
