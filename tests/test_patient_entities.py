import pytest
import re
import os
import filecmp

from proknow import Exceptions

def test_download_image_set(app, workspace_factory, temp_directory):
    pk = app.pk

    image_files = [
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm"),
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00001.dcm"),
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00002.dcm"),
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00003.dcm"),
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00004.dcm"),
    ]
    workspace_factory(("patient-download-image-set-test", "Patient Download Image Set Test", False))
    pk.uploads.upload("Patient Download Image Set Test", image_files)
    patients = pk.patients.lookup("Patient Download Image Set Test", ["HNC-0522c0009"])
    assert len(patients) == 1
    patient = patients[0].get()
    entities = patient.find_entities(type="image_set")
    assert len(entities) == 1
    image_set = entities[0].get()

    # Download to directory
    download_path = image_set.download(temp_directory.path)
    download_image_paths = []
    for _, _, paths in os.walk(download_path):
        for path in paths:
            download_image_paths.append(os.path.join(download_path, path))
    for image_file in image_files:
        for download_image_path in download_image_paths:
            if filecmp.cmp(image_file, download_image_path, shallow=False):
                found = True
                break
        else:
            found = False
        assert found

    # Directory does not exist
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        download_path = image_set.download("/path/to/nowhere/")
    assert err_wrapper.value.message == "`/path/to/nowhere/` is invalid"

def test_download_structure_set(app, workspace_factory, temp_directory):
    pk = app.pk

    structure_set_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    workspace_factory(("patient-download-structure-set-test", "Patient Download Structure Set Test", False))
    pk.uploads.upload("Patient Download Structure Set Test", structure_set_path)
    patients = pk.patients.lookup("Patient Download Structure Set Test", ["HNC-0522c0009"])
    assert len(patients) == 1
    patient = patients[0].get()
    entities = patient.find_entities(type="structure_set")
    assert len(entities) == 1
    structure_set = entities[0].get()

    # Download to directory
    download_path = structure_set.download(temp_directory.path)
    assert filecmp.cmp(structure_set_path, download_path, shallow=False)

    # Download to specific file
    specific_path = os.path.join(temp_directory.path, "structure_set.dcm")
    download_path = structure_set.download(specific_path)
    assert specific_path == download_path
    assert filecmp.cmp(structure_set_path, download_path, shallow=False)

    # File does not exist
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        download_path = structure_set.download("/path/to/nowhere/structure_set.dcm")
    assert err_wrapper.value.message == "`/path/to/nowhere/structure_set.dcm` is invalid"

def test_download_plan(app, workspace_factory, temp_directory):
    pk = app.pk

    plan_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    workspace_factory(("patient-download-plan-test", "Patient Download Plan Test", False))
    pk.uploads.upload("Patient Download Plan Test", plan_path)
    patients = pk.patients.lookup("Patient Download Plan Test", ["HNC-0522c0009"])
    assert len(patients) == 1
    patient = patients[0].get()
    entities = patient.find_entities(type="plan")
    assert len(entities) == 1
    plan = entities[0].get()

    # Download to directory
    download_path = plan.download(temp_directory.path)
    assert filecmp.cmp(plan_path, download_path, shallow=False)

    # Download to specific file
    specific_path = os.path.join(temp_directory.path, "plan.dcm")
    download_path = plan.download(specific_path)
    assert specific_path == download_path
    assert filecmp.cmp(plan_path, download_path, shallow=False)

    # File does not exist
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        download_path = plan.download("/path/to/nowhere/plan.dcm")
    assert err_wrapper.value.message == "`/path/to/nowhere/plan.dcm` is invalid"

def test_download_dose(app, workspace_factory, temp_directory):
    pk = app.pk

    dose_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1_Dose.dcm")
    workspace_factory(("patient-download-dose-test", "Patient Download Dose Test", False))
    pk.uploads.upload("Patient Download Dose Test", dose_path)
    patients = pk.patients.lookup("Patient Download Dose Test", ["HNC-0522c0009"])
    assert len(patients) == 1
    patient = patients[0].get()
    entities = patient.find_entities(type="dose")
    assert len(entities) == 1
    dose = entities[0].get()

    # Download to directory
    download_path = dose.download(temp_directory.path)
    assert filecmp.cmp(dose_path, download_path, shallow=False)

    # Download to specific file
    specific_path = os.path.join(temp_directory.path, "dose.dcm")
    download_path = dose.download(specific_path)
    assert specific_path == download_path
    assert filecmp.cmp(dose_path, download_path, shallow=False)

    # File does not exist
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        download_path = dose.download("/path/to/nowhere/dose.dcm")
    assert err_wrapper.value.message == "`/path/to/nowhere/dose.dcm` is invalid"
