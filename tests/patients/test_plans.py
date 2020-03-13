import six
import pytest
import filecmp
import os

from proknow import Exceptions

def test_download_plan(app, entity_generator, temp_directory):
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
