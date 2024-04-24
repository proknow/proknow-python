import pytest
import filecmp
import os

from proknow import ProKnow, Exceptions

def test_download(app, entity_generator, temp_directory):
    pk = app.pk

    image_files = [
        os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm"),
        os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00001.dcm"),
        os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00002.dcm"),
        os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00003.dcm"),
        os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00004.dcm"),
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

def test_get_refresh(app, entity_generator):
    pk = app.pk

    image_files = [
        os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm"),
    ]
    image_set = entity_generator(image_files)

    old_data = image_set.data
    pk.uploads.upload(image_set._workspace_id, os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00001.dcm"))

    image_set.refresh()
    assert image_set.data != old_data
