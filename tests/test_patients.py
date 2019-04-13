import pytest
import re
import os
import filecmp

from proknow import Exceptions

def test_create_patients(app, workspace_factory):
    pk = app.pk

    workspace_factory(("create-patients-test", "Create Patients Test", False))

    # Verify returned PatientItem
    patient = pk.patients.create("Create Patients Test", "1000", "Last^First", "2018-01-01", "123456.000000", "M")
    assert patient.mrn == "1000"
    assert patient.name == "Last^First"
    assert patient.birth_date == "2018-01-01"
    assert patient.birth_time == "123456.000000"
    assert patient.sex == "M"

    # Assert item can be found in query
    patients = pk.patients.query("Create Patients Test")
    for patient in patients:
        if patient.mrn == "1000":
            patient_match = patient
            break
    else:
        patient_match = None
    assert patient_match is not None
    assert patient_match.mrn == "1000"
    assert patient_match.name == "Last^First"
    assert patient_match.birth_date == "2018-01-01"
    assert patient_match.birth_time == "123456.000000"
    assert patient_match.sex == "M"

def test_create_patients_failure(app, workspace_factory):
    pk = app.pk

    workspace_factory(("create-patients-failure-test", "Create Patients Failure Test", False))

    pk.patients.create("Create Patients Failure Test", "1000", "Last^First")

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.patients.create("Create Patients Failure Test", "1000", "Last^First")
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Patient already exists with mrn "1000"'

def test_delete_patients(app, workspace_factory):
    pk = app.pk

    workspace_factory(("delete-patients-test", "Delete Patients Test", False))
    patient = pk.patients.create("Delete Patients Test", "1000", "Last^First")

    # Verify patient was deleted successfully
    patient.delete()
    for patient in pk.patients.query("Delete Patients Test"):
        if patient.mrn == "1000":
            match = patient
            break
    else:
        match = None
    assert match is None

def test_delete_patients_failure(app, workspace_factory):
    pk = app.pk

    workspace_factory(("delete-patients-failure-test", "Delete Patients Failure Test", False))
    patient = pk.patients.create("Delete Patients Failure Test", "1000", "Last^First")
    patient.delete()

    # Assert error is raised when attempting to delete patient that does not exist
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        patient.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'Patient "' + patient.id + '" not found'

def test_find_patients(app, workspace_factory):
    pk = app.pk

    workspace_factory(("find-patients-test", "Find Patients Test", False))
    pk.patients.create("Find Patients Test", "1000", "Last^First")
    expr = re.compile(r"st\^Fi")

    # Find with no args
    found = pk.patients.find("Find Patients Test")
    assert found is None

    # Find using predicate
    found = pk.patients.find("Find Patients Test", lambda p: expr.search(p.data["name"]) is not None)
    assert found is not None
    assert found.mrn == "1000"
    assert found.name == "Last^First"
    assert found.birth_date == None
    assert found.birth_time == None
    assert found.sex == None

    # Find using props
    found = pk.patients.find("Find Patients Test", mrn="1000", name="Last^First")
    assert found is not None
    assert found.mrn == "1000"
    assert found.name == "Last^First"
    assert found.birth_date == None
    assert found.birth_time == None
    assert found.sex == None

    # Find using both
    found = pk.patients.find("Find Patients Test", lambda p: expr.search(p.data["name"]) is not None, mrn="1000", name="Last^First")
    assert found is not None
    assert found.mrn == "1000"
    assert found.name == "Last^First"
    assert found.birth_date == None
    assert found.birth_time == None
    assert found.sex == None

    # Find failure
    found = pk.patients.find("Find Patients Test", lambda p: expr.search(p.data["mrn"]) is not None)
    assert found is None
    found = pk.patients.find("Find Patients Test", mrn="1000", name="last^first")
    assert found is None

def test_lookup_patients(app, workspace_factory):
    pk = app.pk

    workspace_factory(("lookup-patients-test", "Lookup Patients Test", False))
    pk.patients.create("Lookup Patients Test", "1000", "Test^1", "2018-01-01", "123456.000000", "M")
    pk.patients.create("Lookup Patients Test", "1001", "Test^2")

    patients = pk.patients.lookup("Lookup Patients Test", ["1000", "1001"])
    assert len(patients) == 2
    for patient in patients:
        if patient.mrn == "1000":
            assert patient.mrn == "1000"
            assert patient.name == "Test^1"
            assert patient.birth_date == "2018-01-01"
            assert patient.birth_time == "123456.000000"
            assert patient.sex == "M"
        elif patient.mrn == "1001":
            assert patient.mrn == "1001"
            assert patient.name == "Test^2"
            assert patient.birth_date == None
            assert patient.birth_time == None
            assert patient.sex == None

def test_query_patients(app, workspace_factory):
    pk = app.pk

    workspace_factory(("query-patients-test", "Query Patients Test", False))
    pk.patients.create("Query Patients Test", "1000", "Test^1", "2018-01-01", "123456.000000", "M")
    pk.patients.create("Query Patients Test", "1001", "Test^2")

    # Verify test 1
    for patient in pk.patients.query("Query Patients Test"):
        if patient.mrn == "1000":
            match = patient
            break
    else:
        match = None
    assert match is not None
    assert match.mrn == "1000"
    assert match.name == "Test^1"
    assert match.birth_date == "2018-01-01"
    assert match.birth_time == "123456.000000"
    assert match.sex == "M"

    # Verify test 2
    for patient in pk.patients.query("Query Patients Test"):
        if patient.mrn == "1001":
            match = patient
            break
    else:
        match = None
    assert match is not None
    assert match.mrn == "1001"
    assert match.name == "Test^2"
    assert match.birth_date == None
    assert match.birth_time == None
    assert match.sex == None

def test_update_patients(app, custom_metric_factory, workspace_factory):
    pk = app.pk

    custom_metric_factory(("String Metric 1", "patient", {"string": {}}))
    custom_metric_factory(("Numeric Metric 1", "patient", {"number": {}}))
    custom_metric_factory(("Enum Metric 1", "patient", {"enum": {"values": ["one", "two"]}}))
    workspace_factory(("update-patients-test", "Update Patients Test", False))
    patient = pk.patients.create("Update Patients Test", "1000", "Last^First")

    # Verify patient was updated successfully
    patient.mrn = "1000-AAAA-2000"
    patient.name = "Modified^Name"
    patient.birth_date = "2018-01-01"
    patient.birth_time = "123456.000000"
    patient.sex = "M"
    meta = patient.get_metadata()
    meta["String Metric 1"] = "test"
    meta["Numeric Metric 1"] = 42
    meta["Enum Metric 1"] = "one"
    patient.set_metadata(meta)
    patient.save()
    patients = pk.patients.query("Update Patients Test")
    for patient in patients:
        if patient.mrn == "1000-AAAA-2000":
            patient_match = patient
            break
    else:
        patient_match = None
    assert patient_match is not None
    patient_item = patient_match.get()
    assert patient_item.mrn == "1000-AAAA-2000"
    assert patient_item.name == "Modified^Name"
    assert patient_item.birth_date == "2018-01-01"
    assert patient_item.birth_time == "123456.000000"
    assert patient_item.sex == "M"
    assert patient_item.get_metadata() == {
        "String Metric 1": "test",
        "Numeric Metric 1": 42,
        "Enum Metric 1": "one"
    }

def test_update_patients_failure(app, workspace_factory):
    pk = app.pk

    workspace_factory(("update-patients-failure-test", "Update Patients Failure Test", False))
    patient1 = pk.patients.create("Update Patients Failure Test", "1000", "Last^First")
    patient2 = pk.patients.create("Update Patients Failure Test", "1001", "Last^First")

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        patient1.mrn = "1001"
        patient1.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Patient already exists with mrn "1001"'

def test_patient_set_metadata_failure(app, workspace_factory):
    pk = app.pk

    workspace_factory(("patient-set-metadata-failure-test", "Patient Set Metadata Failure Test", False))
    patient = pk.patients.create("Patient Set Metadata Failure Test", "1000", "Last^First")
    meta = patient.get_metadata()
    meta["Unknown Metric"] = "test"

    with pytest.raises(Exceptions.CustomMetricLookupError) as err_wrapper:
        patient.set_metadata(meta)
    assert err_wrapper.value.message == 'Custom metric with name `Unknown Metric` not found.'

def test_patient_find_entities(app, workspace_factory):
    pk = app.pk

    workspace_factory(("patient-find-entities-test", "Patient Find Entities Test", False))
    pk.uploads.upload("Patient Find Entities Test", "./tests/data/Becker^Matthew")
    patients = pk.patients.lookup("Patient Find Entities Test", ["HNC-0522c0009"])
    assert len(patients) == 1
    patient = patients[0].get()
    entities = patient.find_entities()
    assert len(entities) == 0
    entities = patient.find_entities(lambda entity: True)
    assert len(entities) == 4
    entities = patient.find_entities(lambda entity: entity.data["type"] == "dose" or entity.data["type"] == "plan")
    assert len(entities) == 2
    entities = patient.find_entities(type="dose")
    assert len(entities) == 1

def test_create_patient_scorecards(app, workspace_factory, custom_metric_factory):
    pk = app.pk

    workspace_factory(("patient-scorecards-create-test", "Patient Scorecards Create Test", False))
    custom_metric_factory(("Numeric Metric (Scorecard Create)", "patient", {"number": {}}))
    pk.uploads.upload("Patient Scorecards Create Test", "./tests/data/Becker^Matthew")
    patients = pk.patients.lookup("Patient Scorecards Create Test", ["HNC-0522c0009"])
    patient = patients[0].get()
    entities = patient.find_entities(type="dose")
    entity = entities[0].get()

    scorecard = entity.scorecards.create("My Scorecard", [], [])
    assert scorecard.name == "My Scorecard"
    assert len(scorecard.computed) == 0
    assert len(scorecard.custom) == 0

    scorecard = entity.scorecards.create("My Scorecard 2", [{
        "type": "VOLUME",
        "roi_name": "BRAINSTEM",
        "arg_1": None,
        "arg_2": None
    }, {
        "type": "VOLUME_CC_DOSE_RANGE_ROI",
        "roi_name": "BRAINSTEM",
        "arg_1": 30,
        "arg_2": 60,
        "objectives": [{
            "label": "IDEAL",
            "color": [18, 191, 0],
            "max": 0
        }, {
            "label": "GOOD",
            "color": [136, 223, 127],
            "max": 3
        }, {
            "label": "ACCEPTABLE",
            "color": [255, 216, 0],
            "max": 6
        }, {
            "label": "MARGINAL",
            "color": [255, 102, 0],
            "max": 9
        }, {
            "label": "UNACCEPTABLE",
            "color": [255, 0, 0]
        }]
    }], [{
        "id": pk.custom_metrics.resolve_by_name("Numeric Metric (Scorecard Create)").id
    }])
    assert scorecard.name == "My Scorecard 2"
    assert len(scorecard.computed) == 2
    assert len(scorecard.custom) == 1

def test_create_patient_scorecards_failure(app, workspace_factory):
    pk = app.pk

    workspace_factory(("patient-scorecards-create-test-failure", "Patient Scorecards Create Failure Test", False))
    pk.uploads.upload("Patient Scorecards Create Failure Test", "./tests/data/Becker^Matthew")
    patients = pk.patients.lookup("Patient Scorecards Create Failure Test", ["HNC-0522c0009"])
    patient = patients[0].get()
    entities = patient.find_entities(type="dose")
    entity = entities[0].get()
    scorecard = entity.scorecards.create("My Scorecard", [], [])

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        entity.scorecards.create("My Scorecard", [], [])
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Entity metric set already exists with name "My Scorecard"'

def test_delete_patient_scorecards(app, workspace_factory):
    pk = app.pk

    workspace_factory(("patient-scorecards-delete-test", "Patient Scorecards Delete Test", False))
    pk.uploads.upload("Patient Scorecards Delete Test", "./tests/data/Becker^Matthew")
    patients = pk.patients.lookup("Patient Scorecards Delete Test", ["HNC-0522c0009"])
    patient = patients[0].get()
    entities = patient.find_entities(type="dose")
    entity = entities[0].get()
    scorecard = entity.scorecards.create("My Scorecard", [], [])

    # Verify scorecard was deleted successfully
    scorecard.delete()
    for scorecard in entity.scorecards.query():
        if scorecard.name == "My Scorecard":
            match = scorecard
            break
    else:
        match = None
    assert match is None

def test_delete_patient_scorecards_failure(app, workspace_factory):
    pk = app.pk

    workspace_factory(("patient-scorecards-delete-failure-test", "Patient Scorecards Delete Failure Test", False))
    pk.uploads.upload("Patient Scorecards Delete Failure Test", "./tests/data/Becker^Matthew")
    patients = pk.patients.lookup("Patient Scorecards Delete Failure Test", ["HNC-0522c0009"])
    patient = patients[0].get()
    entities = patient.find_entities(type="dose")
    entity = entities[0].get()
    scorecard = entity.scorecards.create("My Scorecard", [], [])
    scorecard.delete()

    # Assert error is raised when attempting to delete scorecard that does not exist
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        scorecard.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'Metric set "' + scorecard.id + '" not found in entity "' + entity.id + '"'

def test_find_patient_scorecards(app, workspace_factory):
    pk = app.pk

    workspace_factory(("find-patient-scorecards-test", "Find Patient Scorecards Test", False))
    pk.uploads.upload("Find Patient Scorecards Test", "./tests/data/Becker^Matthew")
    patients = pk.patients.lookup("Find Patient Scorecards Test", ["HNC-0522c0009"])
    patient = patients[0].get()
    entities = patient.find_entities(type="dose")
    entity = entities[0].get()
    scorecard = entity.scorecards.create("Find Scorecards Test", [], [])
    expr = re.compile(r"nd Score")
    expr2 = re.compile(r"score")

    # Find with no args
    found = entity.scorecards.find()
    assert found is None

    # Find using predicate
    found = entity.scorecards.find(lambda p: expr.search(p.data["name"]) is not None)
    assert found is not None
    assert found.name == "Find Scorecards Test"
    scorecard = found.get()
    assert len(scorecard.computed) == 0
    assert len(scorecard.custom) == 0

    # Find using props
    found = entity.scorecards.find(name="Find Scorecards Test")
    assert found is not None
    assert found.name == "Find Scorecards Test"
    scorecard = found.get()
    assert len(scorecard.computed) == 0
    assert len(scorecard.custom) == 0

    # Find using both
    found = entity.scorecards.find(lambda p: expr.search(p.data["name"]) is not None, name="Find Scorecards Test")
    assert found is not None
    assert found.name == "Find Scorecards Test"
    scorecard = found.get()
    assert len(scorecard.computed) == 0
    assert len(scorecard.custom) == 0

    # Find failure
    found = entity.scorecards.find(lambda p: expr2.search(p.data["name"]) is not None)
    assert found is None
    found = entity.scorecards.find(name="Find Scorecards")
    assert found is None

def test_query_patient_scorecards(app, workspace_factory):
    pk = app.pk

    workspace_factory(("query-patient-scorecards-test", "Query Patient Scorecards Test", False))
    pk.uploads.upload("Query Patient Scorecards Test", "./tests/data/Becker^Matthew")
    patients = pk.patients.lookup("Query Patient Scorecards Test", ["HNC-0522c0009"])
    patient = patients[0].get()
    entities = patient.find_entities(type="dose")
    entity = entities[0].get()
    scorecard = entity.scorecards.create("My Scorecard 1", [], [])
    scorecard = entity.scorecards.create("My Scorecard 2", [], [])

    # Verify scorecard 1
    for scorecard in entity.scorecards.query():
        if scorecard.name == "My Scorecard 1":
            match = scorecard
            break
    else:
        match = None
    assert scorecard is not None
    assert scorecard.name == "My Scorecard 1"

    # Verify scorecard 2
    for scorecard in entity.scorecards.query():
        if scorecard.name == "My Scorecard 2":
            match = scorecard
            break
    else:
        match = None
    assert scorecard is not None
    assert scorecard.name == "My Scorecard 2"

def test_update_patient_scorecards(app, workspace_factory, custom_metric_factory):
    pk = app.pk

    workspace_factory(("patient-scorecards-update-test", "Patient Scorecards Update Test", False))
    custom_metric_factory(("Numeric Metric (Scorecard Update)", "patient", {"number": {}}))
    pk.uploads.upload("Patient Scorecards Update Test", "./tests/data/Becker^Matthew")
    patients = pk.patients.lookup("Patient Scorecards Update Test", ["HNC-0522c0009"])
    patient = patients[0].get()
    entities = patient.find_entities(type="dose")
    entity = entities[0].get()
    scorecard = entity.scorecards.create("My Scorecard", [], [])

    # Verify patient scorecard was updated successfully
    scorecard.name = "My Scorecard Updated"
    scorecard.computed = [{
        "type": "VOLUME",
        "roi_name": "BRAINSTEM",
        "arg_1": None,
        "arg_2": None
    }, {
        "type": "VOLUME_CC_DOSE_RANGE_ROI",
        "roi_name": "BRAINSTEM",
        "arg_1": 30,
        "arg_2": 60,
        "objectives": [{
            "label": "IDEAL",
            "color": [18, 191, 0],
            "max": 0
        }, {
            "label": "GOOD",
            "color": [136, 223, 127],
            "max": 3
        }, {
            "label": "ACCEPTABLE",
            "color": [255, 216, 0],
            "max": 6
        }, {
            "label": "MARGINAL",
            "color": [255, 102, 0],
            "max": 9
        }, {
            "label": "UNACCEPTABLE",
            "color": [255, 0, 0]
        }]
    }]
    scorecard.custom = [{
        "id": pk.custom_metrics.resolve_by_name("Numeric Metric (Scorecard Update)").id
    }]
    scorecard.save()
    scorecards = entity.scorecards.query()
    for scorecard in scorecards:
        if scorecard.name == "My Scorecard Updated":
            scorecard_match = scorecard
            break
    else:
        scorecard_match = None
    assert scorecard_match is not None
    scorecard_item = scorecard_match.get()
    assert scorecard_item.name == "My Scorecard Updated"
    assert len(scorecard_item.computed) == 2
    assert len(scorecard_item.custom) == 1

def test_update_patient_scorecards_failure(app, workspace_factory):
    pk = app.pk

    workspace_factory(("patient-scorecards-update-failure-test", "Patient Scorecards Update Failure Test", False))
    pk.uploads.upload("Patient Scorecards Update Failure Test", "./tests/data/Becker^Matthew")
    patients = pk.patients.lookup("Patient Scorecards Update Failure Test", ["HNC-0522c0009"])
    patient = patients[0].get()
    entities = patient.find_entities(type="dose")
    entity = entities[0].get()
    scorecard1 = entity.scorecards.create("My Scorecard 1", [], [])
    scorecard2 = entity.scorecards.create("My Scorecard 2", [], [])

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        scorecard2.name = "My Scorecard 1"
        scorecard2.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Entity metric set already exists with name "My Scorecard 1"'

def test_patient_download_image_set(app, workspace_factory, temp_directory):
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

def test_patient_download_structure_set(app, workspace_factory, temp_directory):
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

def test_patient_download_plan(app, workspace_factory, temp_directory):
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

def test_patient_download_dose(app, workspace_factory, temp_directory):
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
