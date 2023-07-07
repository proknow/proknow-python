import pytest

from proknow import Exceptions

def test_create(app, patient_generator):
    pk = app.pk

    patient = patient_generator("./data/Becker^Matthew")
    dose = patient.find_entities(type="dose")[0]
    operands = [{
        "type": "dose",
        "id": dose.id
    }, {
        "type": "dose",
        "id": dose.id
    }]
    task = patient.tasks.create({
        "type": "dose_composition",
        "name": "Dose Composition",
        "operation": {
            "type": "addition",
            "operands": operands
        }
    })
    task.wait()
    data = task.data
    assert isinstance(data["id"], str)
    assert data["status"] == "completed"
    assert len(data["output"]["entities"]) == 1
    patient = pk.patients.find(patient.workspace_id, mrn=patient.mrn).get()
    doses = patient.find_entities(id=data["output"]["entities"][0]["id"])
    assert len(doses) == 1

def test_delete(app, patient_generator):
    pk = app.pk

    patient = patient_generator("./data/Becker^Matthew")
    dose = patient.find_entities(type="dose")[0]
    operands = [{
        "type": "dose",
        "id": dose.id
    }, {
        "type": "dose",
        "id": dose.id
    }]
    task = patient.tasks.create({
        "type": "dose_composition",
        "name": "ProKnow-CompositeDoses-Error1-kie#MhQ29JS!pJJCj@Qt&bq*$Vp.9axb89",
        "operation": {
            "type": "addition",
            "operands": operands
        }
    })
    task.wait()
    assert task.data["status"] == "failed"
    assert task.data["hidden"] is False
    task.delete()
    assert task.data["status"] == "failed"
    assert task.data["hidden"] is True

def test_get(app, patient_generator):
    pk = app.pk

    patient = patient_generator("./data/Becker^Matthew")
    dose = patient.find_entities(type="dose")[0]
    operands = [{
        "type": "dose",
        "id": dose.id
    }, {
        "type": "dose",
        "id": dose.id
    }]
    task = patient.tasks.create({
        "type": "dose_composition",
        "name": "Dose Composition",
        "operation": {
            "type": "addition",
            "operands": operands
        }
    })
    tasks = patient.tasks.query(hidden=True, wait=True)
    summary = tasks[0]
    assert isinstance(summary.data["id"], str) is True
    assert summary.data["type"] == "dose_composition"
    assert summary.data["status"] == "completed"
    assert summary.data["hidden"] == True
    assert isinstance(summary.data["created_by"], dict)
    assert isinstance(summary.data["created_at"], str)
    assert isinstance(summary.data["resolved_at"], str)
    assert summary.data["failure"] is None
    item = summary.get()
    assert isinstance(item.data["id"], str) is True
    assert item.data["type"] == "dose_composition"
    assert item.data["status"] == "completed"
    assert item.data["hidden"] == True
    assert isinstance(item.data["created_by"], dict)
    assert isinstance(item.data["created_at"], str)
    assert isinstance(item.data["resolved_at"], str)
    assert item.data["failure"] is None
    assert "args" in item.data
    assert "output" in item.data

def test_query(app, patient_generator):
    pk = app.pk

    patient = patient_generator("./data/Becker^Matthew")
    dose = patient.find_entities(type="dose")[0]
    operands = [{
        "type": "dose",
        "id": dose.id
    }, {
        "type": "dose",
        "id": dose.id
    }]
    task = patient.tasks.create({
        "type": "dose_composition",
        "name": "Dose Composition",
        "operation": {
            "type": "addition",
            "operands": operands
        }
    })
    tasks = patient.tasks.query(hidden=True, wait=True)
    assert len(tasks) == 1
    assert tasks[0].id == task.id

    tasks = patient.tasks.query()
    len(tasks) == 0
