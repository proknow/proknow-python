import pytest
import re
import json
import copy
import filecmp
import os
from time import sleep

from pktestconfig import base_url, credentials_id, credentials_secret

from proknow import ProKnow, Exceptions

def test_download(app, entity_generator, temp_directory):
    pk = app.pk

    structure_set_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    structure_set = entity_generator(structure_set_path)

    # Download to directory
    download_path = structure_set.download(temp_directory.path)
    assert filecmp.cmp(structure_set_path, download_path, shallow=False)

    # Download to specific file
    specific_path = os.path.join(temp_directory.path, "structure_set.dcm")
    download_path = structure_set.download(specific_path)
    assert specific_path == download_path
    assert filecmp.cmp(structure_set_path, download_path, shallow=False)

def test_download_failure(app, entity_generator, temp_directory):
    pk = app.pk

    structure_set_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    structure_set = entity_generator(structure_set_path)

    # File does not exist
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        download_path = structure_set.download("/path/to/nowhere/structure_set.dcm")
    assert err_wrapper.value.message == "`/path/to/nowhere/structure_set.dcm` is invalid"

    # Entity is a draft
    with structure_set.draft() as draft:
        with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
            download_path = draft.download(temp_directory.path)
        assert err_wrapper.value.message == "Draft versions of structure sets cannot be downloaded"

def test_rois(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    assert isinstance(structure_set.rois, list)
    structures = [
        ("BODY", "EXTERNAL", [0, 255, 0]),
        ("PAROTID_LT", "ORGAN", [0, 0, 255]),
        ("PTV", "ORGAN", [255, 0, 0])
    ]
    for structure in structures:
        name = structure[0]
        for roi in structure_set.rois:
            if roi.name == name:
                match = roi
                break
        else:
            match = None
        assert match is not None
        assert match.type == structure[1]
        assert match.color == structure[2]
        assert match.is_editable() is False

    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        match.delete()
    assert err_wrapper.value.message == "Item is not editable"

    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        match.save()
    assert err_wrapper.value.message == "Item is not editable"

def test_rois_get_data(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    for roi in structure_set.rois:
        if roi.name == "PTV":
            match = roi
            break
    else:
        match = None
    assert match is not None
    roi_data = match.get_data()
    assert roi_data.is_editable() is False
    with open("./tests/data/Becker^Matthew-data/structure_data_PTV.json", 'r') as file:
        data = json.load(file)
        assert roi_data.contours == data["contours"]
        assert roi_data.lines == data["lines"]
        assert roi_data.points == data["points"]

    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        roi_data.save()
    assert err_wrapper.value.message == "Item is not editable"

def test_draft(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")

    # With context manager
    with structure_set.draft() as draft:
        assert draft.is_draft() is True
        assert draft.is_editable() is True
        assert draft._renewer is not None

        draft._renewer.start()
        draft._renewer.stop()
        draft._renewer.stop()
        draft._renewer.start()

    # Without context manager
    draft = structure_set.draft()
    assert draft.is_draft() is True
    assert draft.is_editable() is True
    assert draft._renewer is None
    draft.start_renewer()
    assert draft._renewer is not None
    draft.stop_renewer()
    assert draft._renewer is None

    # Test renewer
    structure_set.start_renewer()
    assert structure_set._renewer is None
    structure_set.stop_renewer()
    assert structure_set._renewer is None

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    pk.patients.delete(structure_set.workspace_id, structure_set.patient_id)
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        structure_set.draft()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'Structure set "' + structure_set.id + '" not found'

def test_lock_renewal(app, entity_generator):
    pk = app.pk
    pk.LOCK_RENEWAL_BUFFER = 358

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    with structure_set.draft() as draft:
        i = 0
        expires_at_initial = draft._lock["expires_at"]
        while True:
            if expires_at_initial != draft._lock["expires_at"]:
                break
            elif i > 50:
                raise ValueError('Timeout waiting for lock to renew')
            else:
                sleep(0.1)
            i += 1
        assert expires_at_initial != draft._lock["expires_at"]

    pk.LOCK_RENEWAL_BUFFER = 30

def test_draft_edit(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew", type="structure_set")
    with structure_set.draft() as draft:
        assert len(draft.rois) == 3

        # Discard the PAROTID_LT structure
        for roi in draft.rois:
            if roi.name == "PAROTID_LT":
                match = roi
                break
        else:
            match = None
        assert match is not None
        match.delete()
        assert len(draft.rois) == 2

        # Edit the name, color, and type of PTV structure
        for roi in draft.rois:
            if roi.name == "PTV":
                match = roi
                break
        else:
            match = None
        assert match is not None
        match.name = "PTV2"
        match.color = [255, 147, 0]
        match.type = "PTV"
        match.save()

        # Create a new structure
        item = draft.create_roi('PATIENT', [0, 238, 255], 'EXTERNAL')
        assert len(draft.rois) == 3
        data = item.get_data()
        for roi in draft.rois:
            if roi.name == "BODY":
                match = roi
                break
        else:
            match = None
        data.contours = copy.deepcopy(match.get_data().contours)
        data.save()

        # Modify existing contour data
        for roi in draft.rois:
            if roi.name == "BODY":
                match = roi
                break
        else:
            match = None
        data = match.get_data()
        contours = data.contours
        modified = []
        for contour in contours:
            modified_contours = { 'pos': contour["pos"], 'paths': [] }
            for path in contour["paths"]:
                modified_path = []
                i = 0
                length = len(path)
                while i < length:
                    modified_path.extend([path[i], path[i+1]])
                    i += 4 # skip every other pair
                modified_contours["paths"].append(modified_path)
            modified.append(modified_contours)
        contours = modified
        data.save()

        # Approve draft
        structure_set = draft.approve("test 1 label", "test 1 message")

    # Verify approved structure set
    assert isinstance(structure_set.rois, list)
    structures = [
        ("BODY", "EXTERNAL", [0, 255, 0]),
        ("PTV2", "PTV", [255, 147, 0]),
        ("PATIENT", "EXTERNAL", [0, 238, 255])
    ]
    for structure in structures:
        name = structure[0]
        for roi in structure_set.rois:
            if roi.name == name:
                match = roi
                break
        else:
            match = None
        assert match is not None
        assert match.type == structure[1]
        assert match.color == structure[2]
        assert match.is_editable() is False

def test_discard(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    with structure_set.draft() as draft:
        draft.discard()
    assert len(structure_set.versions.query()) == 1

def test_approve_failure(app, entity_generator):
    pk = app.pk

    structure_set_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    structure_set = entity_generator(structure_set_path)
    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        structure_set.approve()
    assert err_wrapper.value.message == "Item is not editable"

def test_create_roi_failure(app, entity_generator):
    pk = app.pk

    structure_set_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    structure_set = entity_generator(structure_set_path)
    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        structure_set.create_roi("test", [123, 0, 123], "ORGAN")
    assert err_wrapper.value.message == "Item is not editable"

def test_discard_failure(app, entity_generator):
    pk = app.pk

    structure_set_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    structure_set = entity_generator(structure_set_path)
    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        structure_set.discard()
    assert err_wrapper.value.message == "Item is not editable"

def test_versions_query(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    with structure_set.draft() as draft:
        structure_set = draft.approve()
    with structure_set.draft() as draft:
        pass

    versions = structure_set.versions.query()
    assert len(versions) == 3
    assert versions[0].status == "draft"
    assert versions[1].status == "approved"
    assert versions[2].status == "archived"

def test_version_download(app, entity_generator, temp_directory):
    pk = app.pk

    structure_set_path = os.path.abspath("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    structure_set = entity_generator("./tests/data/Becker^Matthew", type="structure_set")
    version = structure_set.versions.query()[0]

    # Download to directory
    download_path = version.download(temp_directory.path)
    assert filecmp.cmp(structure_set_path, download_path, shallow=False)

    # Download to specific file
    specific_path = os.path.join(temp_directory.path, "structure_set.dcm")
    download_path = version.download(specific_path)
    assert specific_path == download_path
    assert filecmp.cmp(structure_set_path, download_path, shallow=False)

    # File does not exist
    with pytest.raises(Exceptions.InvalidPathError) as err_wrapper:
        download_path = version.download("/path/to/nowhere/structure_set.dcm")
    assert err_wrapper.value.message == "`/path/to/nowhere/structure_set.dcm` is invalid"

    # Create draft
    with structure_set.draft() as draft:
        pass

    draft_version = structure_set.versions.query()[0]
    # Invalid operation on draft
    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        download_path = draft_version.download(temp_directory.path)
    assert err_wrapper.value.message == "Draft versions of structure sets cannot be downloaded"

    # Approve draft
    with structure_set.draft() as draft:
        structure_set = draft.approve()

    # Verify download completes
    download_path = structure_set.versions.query()[0].download(temp_directory.path)

    # Approve draft with no rois
    with structure_set.draft() as draft:
        rois = draft.rois[:]
        for roi in rois:
            roi.delete()
        structure_set = draft.approve()

    # Verify download error
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        download_path = structure_set.versions.query()[0].download(temp_directory.path)
    assert err_wrapper.value.status_code == 400
    assert err_wrapper.value.body == 'Structure set is empty.'

def test_version_delete(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    with structure_set.draft() as draft:
        structure_set = draft.approve()
    with structure_set.draft() as draft:
        pass

    versions = structure_set.versions.query()
    archived_version = versions[-1]
    archived_version.delete()

    draft_version = versions[0]
    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        draft_version.delete()
    assert err_wrapper.value.message == "Draft versions of structure sets cannot be deleted"

def test_version_get(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    with structure_set.draft() as draft:
        structure_set = draft.approve()
    with structure_set.draft() as draft:
        pass

    versions = structure_set.versions.query()
    assert len(versions) == 3
    draft_version = versions[0].get()
    assert draft_version.is_editable() is False
    assert draft_version.is_draft() is True
    assert draft_version.rois is not None
    approved_version = versions[1].get()
    assert approved_version.is_editable() is False
    assert approved_version.is_draft() is False
    assert approved_version.rois is not None
    archived_version = versions[2].get()
    assert archived_version.is_editable() is False
    assert archived_version.is_draft() is False
    assert archived_version.rois is not None

def test_version_revert(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    with structure_set.draft() as draft:
        structure_set = draft.approve()
    with structure_set.draft() as draft:
        pass

    versions = structure_set.versions.query()
    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        draft_version = versions[0].revert()
    assert err_wrapper.value.message == "Draft versions of structure sets cannot be reverted"

    with structure_set.draft() as draft:
        draft.discard()

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        approved_version = versions[1].revert()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Structure set version "' + versions[1].id + '" for structure set "' + structure_set.id + '" is already approved'

    structure_set = versions[2].revert()
    versions = structure_set.versions.query()
    assert len(versions) == 3
    assert versions[0].status == 'approved'
    assert versions[1].status == 'archived'
    assert versions[2].status == 'archived'

def test_version_save(app, entity_generator):
    pk = app.pk

    structure_set = entity_generator("./tests/data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm", type="structure_set")
    with structure_set.draft() as draft:
        structure_set = draft.approve()
    with structure_set.draft() as draft:
        pass

    versions = structure_set.versions.query()
    draft_version = versions[0]
    with pytest.raises(Exceptions.InvalidOperationError) as err_wrapper:
        draft_version.label = "test label"
        draft_version.message = "test message"
        draft_version.save()
    assert err_wrapper.value.message == "Draft versions of structure sets cannot be saved"

    approved_version = versions[1]
    approved_version.label = "test label (approved)"
    approved_version.message = "test message (approved)"
    approved_version.save()

    archived_version = versions[2]
    archived_version.label = "test label (archived)"
    archived_version.message = "test message (archived)"
    archived_version.save()

    # Query again and verify
    versions = structure_set.versions.query()
    draft_version = versions[0]
    assert draft_version.label is None
    assert draft_version.message is None
    assert draft_version.data["imported"] is False
    approved_version = versions[1]
    assert approved_version.label == "test label (approved)"
    assert approved_version.message == "test message (approved)"
    assert approved_version.data["imported"] is False
    archived_version = versions[2]
    assert archived_version.label == "test label (archived)"
    assert archived_version.message == "test message (archived)"
    assert archived_version.data["imported"] is True
