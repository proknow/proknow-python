import pytest
import re
import os
import filecmp

from proknow import Exceptions

def test_download_image_set(app, entity_generator, temp_directory):
    pk = app.pk

    image_files = [
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm"),
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00001.dcm"),
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00002.dcm"),
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00003.dcm"),
        os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_CT1_image00004.dcm"),
    ]
    image_set = entity_generator(image_files)

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

def test_download_plan(app, entity_generator, temp_directory):
    pk = app.pk

    plan_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
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

def test_download_dose(app, entity_generator, temp_directory):
    pk = app.pk

    dose_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_Plan1_Dose.dcm")
    dose = entity_generator(dose_path)

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
