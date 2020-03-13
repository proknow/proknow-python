import pytest
import re
import os
import filecmp
import six

from proknow import Exceptions

def test_delete_entity_summary(app, workspace_generator):
    pk = app.pk

    directory = os.path.abspath("./data/Becker^Matthew/")
    _, workspace = workspace_generator()
    batch = pk.uploads.upload(workspace.id, directory)
    assert len(batch.patients) == 1
    patient_id = batch.patients[0].id

    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 4
    image_set = patient.find_entities(type="image_set")[0]
    image_set.delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 3
    assert len(patient.find_entities(type="image_set")) == 0

    structure_set = patient.find_entities(type="structure_set")[0]
    structure_set.delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 2
    assert len(patient.find_entities(type="structure_set")) == 0

    plan = patient.find_entities(type="plan")[0]
    plan.delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 1
    assert len(patient.find_entities(type="plan")) == 0

    dose = patient.find_entities(type="dose")[0]
    dose.delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 0

def test_delete_entity_item(app, workspace_generator):
    pk = app.pk

    directory = os.path.abspath("./data/Becker^Matthew/")
    _, workspace = workspace_generator()
    batch = pk.uploads.upload(workspace.id, directory)
    assert len(batch.patients) == 1
    patient_id = batch.patients[0].id

    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 4
    image_set = patient.find_entities(type="image_set")[0]
    image_set.get().delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 3
    assert len(patient.find_entities(type="image_set")) == 0

    structure_set = patient.find_entities(type="structure_set")[0]
    structure_set.get().delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 2
    assert len(patient.find_entities(type="structure_set")) == 0

    plan = patient.find_entities(type="plan")[0]
    plan.get().delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 1
    assert len(patient.find_entities(type="plan")) == 0

    dose = patient.find_entities(type="dose")[0]
    dose.get().delete()
    patient = pk.patients.get(workspace.id, patient_id)
    assert len(patient.find_entities(lambda entity: True)) == 0

def test_download_image_set(app, entity_generator, temp_directory):
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

def test_image_set_get_image_data(app, entity_generator):
    pk = app.pk

    image_files = [
        os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm"),
    ]
    image_set = entity_generator(image_files)

    data = image_set.get_image_data(0)
    assert isinstance(data, six.binary_type), "data is not binary"

def test_update(app, entity_generator, custom_metric_generator):
    pk = app.pk

    _, custom_metric_image_set = custom_metric_generator(context="image_set", type={"number": {}})
    _, custom_metric_structure_set = custom_metric_generator(context="structure_set", type={"number": {}})
    _, custom_metric_plan = custom_metric_generator(context="plan", type={"number": {}})
    _, custom_metric_dose = custom_metric_generator(context="dose", type={"number": {}})
    image_set_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm")
    structure_set_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_StrctrSets.dcm")
    plan_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1.dcm")
    dose_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1_Dose.dcm")
    image_set = entity_generator(image_set_path)
    structure_set = entity_generator(structure_set_path)
    plan = entity_generator(plan_path)
    dose = entity_generator(dose_path)

    # Update image set entity
    image_set.description = "image set description test 1"
    meta = image_set.get_metadata()
    meta[custom_metric_image_set.name] = 1
    image_set.set_metadata(meta)
    image_set.save()
    patient = pk.patients.get(image_set.workspace_id, image_set.patient_id)
    image_set_entity = patient.find_entities(id=image_set.id)[0].get()
    assert image_set_entity.description == "image set description test 1"
    assert image_set_entity.get_metadata() == {
        custom_metric_image_set.name: 1
    }

    # Update structure set entity
    structure_set.description = "structure set description test 2"
    meta = structure_set.get_metadata()
    meta[custom_metric_structure_set.name] = 2
    structure_set.set_metadata(meta)
    structure_set.save()
    patient = pk.patients.get(structure_set.workspace_id, structure_set.patient_id)
    structure_set_entity = patient.find_entities(id=structure_set.id)[0].get()
    assert structure_set_entity.description == "structure set description test 2"
    assert structure_set_entity.get_metadata() == {
        custom_metric_structure_set.name: 2
    }

    # Update plan entity
    plan.description = "plan description test 3"
    meta = plan.get_metadata()
    meta[custom_metric_plan.name] = 3
    plan.set_metadata(meta)
    plan.save()
    patient = pk.patients.get(plan.workspace_id, plan.patient_id)
    plan_entity = patient.find_entities(id=plan.id)[0].get()
    assert plan_entity.description == "plan description test 3"
    assert plan_entity.get_metadata() == {
        custom_metric_plan.name: 3
    }

    # Update dose entity
    dose.description = "dose description test 4"
    meta = dose.get_metadata()
    meta[custom_metric_dose.name] = 4
    dose.set_metadata(meta)
    dose.save()
    patient = pk.patients.get(dose.workspace_id, dose.patient_id)
    dose_entity = patient.find_entities(id=dose.id)[0].get()
    assert dose_entity.description == "dose description test 4"
    assert dose_entity.get_metadata() == {
        custom_metric_dose.name: 4
    }

def test_update_failure(app, entity_generator):
    pk = app.pk

    image_set_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm")
    image_set = entity_generator(image_set_path)
    image_set.delete()

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        image_set.description = "test"
        image_set.save()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'Entity "' + image_set.id + '" not found in workspace "' + image_set.workspace_id + '"'

def test_set_metadata_failure(app, entity_generator):
    pk = app.pk

    image_set_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_CT1_image00000.dcm")
    image_set = entity_generator(image_set_path)
    meta = image_set.get_metadata()
    meta["Unknown Metric"] = "test"

    with pytest.raises(Exceptions.CustomMetricLookupError) as err_wrapper:
        image_set.set_metadata(meta)
    assert err_wrapper.value.message == 'Custom metric with name `Unknown Metric` not found.'
