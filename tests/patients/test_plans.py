import pytest
import filecmp
import os

from proknow import ProKnow, Exceptions

def test_download(app, entity_generator, temp_directory):
    pk = app.pk

    plan_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    plan = entity_generator(plan_path)

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

def test_get_delivery_information(app, entity_generator):
    pk = app.pk

    plan_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    plan = entity_generator(plan_path)

    info = plan.get_delivery_information()
    assert "equipment" in info
    assert "patient_setups" in info
    assert "fraction_groups" in info
    assert "beams" in info
    assert "brachy" in info

def test_refresh(app, patient_generator):
    pk = app.pk

    patient = patient_generator([
        "./data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm",
        "./data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm",
        "./data/Becker^Matthew/HNC0522c0009_Plan1.dcm"
    ])
    plan = patient.find_entities(type="plan")[0].get()
    structure_set = patient.find_entities(type="structure_set")[0]
    image_set = patient.find_entities(type="image_set")[0]
    old_data = plan.data
    plan.update_parent(image_set) # This calls refresh internally
    assert plan.data != old_data
