import pytest
import re
import os
import filecmp

from proknow import Exceptions

def test_delete_sro_summary(app, workspace_generator):
    pk = app.pk

    directory = os.path.abspath("./data/Registration/")
    _, workspace = workspace_generator()
    batch = pk.uploads.upload(workspace.id, directory)
    assert len(batch.patients) == 1
    patient_id = batch.patients[0].id

    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_sros(lambda entity: True)) == 3
    sro = patient.find_sros(name="Identity Matrix")[0]
    sro.delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_sros(lambda entity: True)) == 2
    assert len(patient.find_sros(name="Identity Matrix")) == 0

def test_delete_sro_item(app, workspace_generator):
    pk = app.pk

    directory = os.path.abspath("./data/Registration/")
    _, workspace = workspace_generator()
    batch = pk.uploads.upload(workspace.id, directory)
    assert len(batch.patients) == 1
    patient_id = batch.patients[0].id

    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_sros(lambda entity: True)) == 3
    sro = patient.find_sros(name="Identity Matrix")[0]
    sro.get().delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_sros(lambda entity: True)) == 2
    assert len(patient.find_sros(name="Identity Matrix")) == 0

def test_get(app, workspace_generator):
    pk = app.pk

    path = os.path.abspath("./data/Registration/reg_identity.dcm")

    directory = os.path.abspath("./data/Registration/")
    _, workspace = workspace_generator()
    batch = pk.uploads.upload(workspace.id, directory)
    patient_upload_summary = batch.find_patient(path)
    sro_upload_summary = batch.find_sro(path)

    patient = pk.patients.get(workspace.id, patient_upload_summary.id)
    sro_summary = patient.find_sros(id=sro_upload_summary.id)[0]
    assert sro_summary.id == sro_upload_summary.id
    sro = sro_summary.get()
    assert sro.id == sro_upload_summary.id
    assert sro.workspace_id == workspace.id
    assert sro.patient_id == patient.id
    assert sro.data["rigid"]["matrix"] == [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1,
    ]

def test_download(app, sro_generator, temp_directory):
    pk = app.pk

    sro_path = os.path.abspath("./data/Registration/reg_identity.dcm")
    sro = sro_generator(sro_path)

    # Download to directory
    download_path = sro.download(temp_directory.path)
    assert filecmp.cmp(sro_path, download_path, shallow=False)

    # Download to specific file
    specific_path = os.path.join(temp_directory.path, "sro.dcm")
    download_path = sro.download(specific_path)
    assert specific_path == download_path
    assert filecmp.cmp(sro_path, download_path, shallow=False)

    # File does not exist
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        download_path = sro.download("/path/to/nowhere/sro.dcm")
    assert err_wrapper.value.message == "`/path/to/nowhere/sro.dcm` is invalid"
