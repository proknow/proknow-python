import pytest
import datetime

from proknow.Audit import Audit
from proknow.Exceptions import HttpError

def test_query(app, user_generator):
    audit = Audit(app.pk, app.pk.requestor)

    user_generator()

    results = audit.query(page_size=1)
    assert results.total > 0

def test_empty_next(app, workspace_generator):
    audit = Audit(app.pk, app.pk.requestor)

    params, workspace = workspace_generator()

    results = audit.query(page_size=1, workspace_id=workspace.id)
    assert results.total == 1
    results = results.next()
    assert len(results.items) == 0
    results = results.next()

def test_next_uses_first_id(app, role_generator):
    audit = Audit(app.pk, app.pk.requestor)

    role_generator()

    results = audit.query(page_size=2)
    assert len(results.items) > 0
    first_time = datetime.datetime.strptime(results.items[0]["timestamp"],"%Y-%m-%dT%H:%M:%S.%fZ")
    assert results.items[0]["id"] == results._options["first_id"]

    role_generator()

    results = results.next()
    result_time = datetime.datetime.strptime(results.items[0]["timestamp"],"%Y-%m-%dT%H:%M:%S.%fZ")
    # All items returned by next should have a timestamp after the first_id's timestamp
    assert  first_time >= result_time

def test_page_size(app, user_generator):
    audit = Audit(app.pk, app.pk.requestor)

    user_generator()

    results = audit.query(page_size=1)
    assert len(results.items) == 1

def test_page_next(app, user_generator):
    audit = Audit(app.pk, app.pk.requestor)

    user_generator()
    user_generator()

    results1 = audit.query(page_size=2)
    
    results2 = audit.query(page_size=1)
    first_id = results2.items[0]["id"]
    results2 = results2.next()
    second_id = results2.items[0]["id"]

    assert first_id != second_id
    assert first_id == results1.items[0]["id"]
    assert second_id == results1.items[1]["id"]

def test_page_number(app, user_generator):
    audit = Audit(app.pk, app.pk.requestor)

    user_generator()

    page1 = audit.query(page_size=1)
    page2 = page1.next()
    otherPage2 = page1.next()
    page3 = page2.next()

    assert page1._options["page_number"] == 0
    assert page2._options["page_number"] == 1
    assert otherPage2._options["page_number"] == 1
    assert page2.items[0]["id"] == otherPage2.items[0]["id"]
    assert page3._options["page_number"] == 2

def test_start_time(app, user_generator):
    audit = Audit(app.pk, app.pk.requestor)

    user_generator()
    now = datetime.datetime.now()
    user_generator()

    results = audit.query(page_size=2, start_time=now)
    for item in results.items:
        assert datetime.datetime.strptime(item["timestamp"],"%Y-%m-%dT%H:%M:%S.%fZ") >= now 
    
def test_end_time(app, user_generator):
    audit = Audit(app.pk, app.pk.requestor)

    user_generator()
    now = datetime.datetime.now()
    user_generator()

    results = audit.query(page_size=2, end_time=now)
    for item in results.items:
        assert datetime.datetime.strptime(item["timestamp"],"%Y-%m-%dT%H:%M:%S.%fZ") <= now

def test_types(app, workspace_generator, user_generator, role_generator):
    audit = Audit(app.pk, app.pk.requestor)

    workspace_generator()
    user_generator()
    role_generator()

    results = audit.query(page_size=1, types="workspace_created")
    assert results.items[0]["type"] == "workspace_created"
    
    results = audit.query(page_size=2, types=["workspace_created", "user_created"])
    for item in results.items:
        assert item["type"] == "workspace_created" or item["type"] == "user_created"

def test_patient_id(app, patient_generator):
    audit = Audit(app.pk, app.pk.requestor)

    patient1 = patient_generator([
        "./data/Becker^Matthew/HNC0522c0009_Plan1.dcm",
    ])
    patient2 = patient_generator([
        "./data/Jensen^Myrtle/HNC0522c0013_CT1_image00000.dcm",
    ])

    results = audit.query(page_size=1, patient_id=patient1.id)
    assert results.items[0]["patient_id"] == patient1.id
    
    results = audit.query(page_size=1, patient_id=patient2.id)
    assert results.items[0]["patient_id"] == patient2.id

def test_patient_mrn(app, patient_generator):
    audit = Audit(app.pk, app.pk.requestor)

    patient1 = patient_generator([
        "./data/Becker^Matthew/HNC0522c0009_Plan1.dcm",
    ])
    patient2 = patient_generator([
        "./data/Jensen^Myrtle/HNC0522c0013_CT1_image00000.dcm",
    ])

    results = audit.query(page_size=1, patient_mrn=patient1.mrn)
    assert results.items[0]["patient_mrn"] == patient1.mrn
    
    results = audit.query(page_size=1, patient_mrn=patient2.mrn)
    assert results.items[0]["patient_mrn"] == patient2.mrn

def test_workspace_id(app, workspace_generator):
    audit = Audit(app.pk, app.pk.requestor)

    _, workspace1 = workspace_generator()
    _, workspace2 = workspace_generator()

    results = audit.query(page_size=1, workspace_id=workspace1.id)
    assert results.items[0]["workspace_id"] == workspace1.id

    results = audit.query(page_size=1, workspace_id=workspace2.id)
    assert results.items[0]["workspace_id"] == workspace2.id

def test_workspace_name(app, workspace_generator):
    audit = Audit(app.pk, app.pk.requestor)

    _, workspace1 = workspace_generator()
    _, workspace2 = workspace_generator()

    results = audit.query(page_size=1, workspace_name=workspace1.name)
    assert results.items[0]["workspace_name"] == workspace1.name

    results = audit.query(page_size=1, workspace_name=workspace2.name)
    assert results.items[0]["workspace_name"] == workspace2.name

def test_collection_id(app, collection_generator):
    audit = Audit(app.pk, app.pk.requestor)

    _, collection1 = collection_generator()
    _, collection2 = collection_generator()

    for collection in app.pk.collections.query():
        collection.get()

    results = audit.query(page_size=1, collection_id=collection1.id)
    assert results.items[0]["collection_id"] == collection1.id

    results = audit.query(page_size=1, collection_id=collection2.id)
    assert results.items[0]["collection_id"] == collection2.id

def test_resource_id(app, workspace_generator, collection_generator):
    audit = Audit(app.pk, app.pk.requestor)

    workspace_generator()
    collection_generator()

    results = audit.query(page_size=1)
    id1 = results.items[0]["resource_id"]

    assert results.items[0]["resource_id"] == id1

def test_resource_name(app, workspace_generator, collection_generator):
    audit = Audit(app.pk, app.pk.requestor)

    workspace_generator()
    collection_generator()

    results = audit.query(page_size=1)
    name = results.items[0]["resource_name"]

    results = audit.query(page_size=1, resource_name=name)
    assert results.items[0]["resource_name"] == name

def test_methods(app, role_generator):
    audit = Audit(app.pk, app.pk.requestor)

    _, role = role_generator()
    app.pk.roles.get(role.id)

    results = audit.query(page_size=1, methods="get")
    assert results._options["methods"] == ["GET"]
    assert results.items[0]["method"] == "GET"

    results = audit.query(page_size=1, methods="GET")
    assert results._options["methods"] == ["GET"]
    assert results.items[0]["method"] == "GET"

    results = audit.query(page_size=1, methods="post")
    assert results._options["methods"] == ["POST"]
    assert results.items[0]["method"] == "POST"

    results = audit.query(page_size=2, methods=["get", "post"])
    assert results._options["methods"] == ["GET", "POST"]
    assert results.items[0]["method"] == "GET"
    assert results.items[1]["method"] == "POST"

def test_status_codes(app):
    audit = Audit(app.pk, app.pk.requestor)

    results = audit.query(page_size=1, status_codes="200")
    assert results._options["status_codes"] == ["200"]

    results = audit.query(page_size=1, status_codes=["200", "403"])
    assert results._options["status_codes"] == ["200", "403"]

def test_uri(app, role_generator):
    audit = Audit(app.pk, app.pk.requestor)

    role_generator()

    results = audit.query(page_size=1)
    uri = results.items[0]["uri"]
    role_generator()

    results = audit.query(page_size=1, uri=uri)
    assert results.items[0]["uri"] == uri

def test_text(app, user_generator, workspace_generator, patient_generator):
    audit = Audit(app.pk, app.pk.requestor)

    patient = patient_generator([
        "./data/Becker^Matthew/HNC0522c0009_Plan1.dcm",
    ])
    user_generator()
    workspace_generator()

    results = audit.query(page_size=1, text="role")
    assert results._options["text"] == ["role"]
    assert "role" in results.items[0]["type"]

    results = audit.query(page_size=5, text=[patient.name, "role"])
    assert results._options["text"] == [patient.name, "role"]
    for item in results.items:
        assert item["patient_name"] == patient.name or "role" in item["type"]

def test_error_pass_through(app):
    audit = Audit(app.pk, app.pk.requestor)

    with pytest.raises(HttpError) as error_info:
        audit.query(page_size=1, methods="gett")
    assert "[\"0\" must be one of [GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH]]" in str(error_info)
