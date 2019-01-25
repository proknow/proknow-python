import pytest
import re

from proknow import Exceptions

def test_create_custom_metrics(app):
    pk = app.pk

    # Verify returned CustomMetricItem
    custom_metric = pk.custom_metrics.create("Create Test", "patient", {"string": {}})
    app.marked_custom_metrics.append(custom_metric) # mark for removal
    assert custom_metric.name == "Create Test"
    assert custom_metric.context == "patient"
    assert custom_metric.type == {"string": {}}

    # Assert item can be found in query
    custom_metrics = pk.custom_metrics.query()
    for custom_metric in custom_metrics:
        if custom_metric.name == "Create Test":
            custom_metric_match = custom_metric
            break
    else:
        custom_metric_match = None
    assert custom_metric_match is not None
    assert custom_metric_match.name == "Create Test"
    assert custom_metric_match.context == "patient"
    assert custom_metric_match.type == {"string": {}}

def test_create_custom_metrics_failure(app, custom_metric_factory):
    pk = app.pk

    custom_metric_factory(("Duplicate Me 1", "patient", {"string": {}}))

    # Assert error is raised for duplicate custom metric
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.custom_metrics.create("Duplicate Me 1", "patient", {"string": {}})
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Custom metric already exists with name "Duplicate Me 1"'

def test_delete_custom_metrics(app, custom_metric_factory):
    pk = app.pk

    custom_metric = custom_metric_factory(("Delete Me", "patient", {"string": {}}), do_not_mark=True)[0]

    # Verify custom metric was deleted successfully
    custom_metric.delete()
    for custom_metric in pk.custom_metrics.query():
        if custom_metric.name == "Delete Me":
            match = custom_metric
            break
    else:
        match = None
    assert match is None

def test_delete_custom_metrics_failure(app, custom_metric_factory):
    pk = app.pk

    custom_metric = custom_metric_factory(("Delete Me Failure", "patient", {"string": {}}), do_not_mark=True)[0]

    custom_metric.delete()

    # Assert error is raised when attempting to delete protected custom metric
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        custom_metric.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == ("Custom metric '" + custom_metric.id + "' not found")

def test_find_custom_metrics(app, custom_metric_factory):
    pk = app.pk

    custom_metric = custom_metric_factory(("Find Me", "patient", {"string": {}}))[0]
    expr = re.compile(r"ind M")

    # Find using predicate
    found = pk.custom_metrics.find(lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is not None
    assert found.name == "Find Me"
    assert found.context == "patient"
    assert found.type == {"string": {}}

    # Find using props
    found = pk.custom_metrics.find(id=custom_metric.id, name="Find Me")
    assert found is not None
    assert found.name == "Find Me"
    assert found.context == "patient"
    assert found.type == {"string": {}}

    # Find using both
    found = pk.custom_metrics.find(lambda ws: expr.search(ws.data["name"]) is not None, id=custom_metric.id, name="Find Me")
    assert found is not None
    assert found.name == "Find Me"
    assert found.context == "patient"
    assert found.type == {"string": {}}

    # Find failure
    found = pk.custom_metrics.find(lambda ws: expr.search(ws.data["id"]) is not None)
    assert found is None
    found = pk.custom_metrics.find(id=custom_metric.id, name="Find me")
    assert found is None

def test_query_custom_metrics(app, custom_metric_factory):
    pk = app.pk

    custom_metric_factory([
        ("Test 1", "patient", {"string": {}}),
        ("Test 2", "image_set", {"number": {}}),
    ])

    # Verify test 1
    for custom_metric in pk.custom_metrics.query():
        if custom_metric.name == "Test 1":
            match = custom_metric
            break
    else:
        match = None
    assert match is not None
    assert match.name == "Test 1"
    assert match.context == "patient"
    assert match.type == {"string": {}}

    # Verify test 2
    for custom_metric in pk.custom_metrics.query():
        if custom_metric.name == "Test 2":
            match = custom_metric
            break
    else:
        match = None
    assert match is not None
    assert match.name == "Test 2"
    assert match.context == "image_set"
    assert match.type == {"number": {}}

def test_resolve(app, custom_metric_factory):
    pk = app.pk

    custom_metric = custom_metric_factory(("Resolve Test 1", "patient", {"string": {}}))[0]

    # Test resolve by id
    resolved = pk.custom_metrics.resolve(custom_metric.id)
    assert resolved is not None
    assert resolved.name == "Resolve Test 1"
    assert resolved.context == "patient"
    assert resolved.type == {"string": {}}

    # Test resolve by name
    resolved = pk.custom_metrics.resolve("Resolve Test 1")
    assert resolved is not None
    assert resolved.name == "Resolve Test 1"
    assert resolved.context == "patient"
    assert resolved.type == {"string": {}}

def test_resolve_failure(app):
    pk = app.pk

    # Test resolve by id
    with pytest.raises(Exceptions.CustomMetricLookupError) as err_wrapper:
        pk.custom_metrics.resolve("00000000000000000000000000000000")
    assert err_wrapper.value.message == "Custom metric with id `00000000000000000000000000000000` not found."

    # Test resolve by name
    with pytest.raises(Exceptions.CustomMetricLookupError) as err_wrapper:
        pk.custom_metrics.resolve("My Metric")
    assert err_wrapper.value.message == "Custom metric with name `My Metric` not found."

def test_resolve_by_id(app, custom_metric_factory):
    pk = app.pk

    custom_metric = custom_metric_factory(("Resolve By Id Test 1", "patient", {"string": {}}))[0]

    resolved = pk.custom_metrics.resolve_by_id(custom_metric.id)
    assert resolved is not None
    assert resolved.name == "Resolve By Id Test 1"
    assert resolved.context == "patient"
    assert resolved.type == {"string": {}}

def test_resolve_by_id_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.CustomMetricLookupError) as err_wrapper:
        pk.custom_metrics.resolve_by_id("00000000000000000000000000000000")
    assert err_wrapper.value.message == "Custom metric with id `00000000000000000000000000000000` not found."

def test_resolve_by_name(app, custom_metric_factory):
    pk = app.pk

    custom_metric = custom_metric_factory([("Resolve By Name Test 1", "patient", {"string": {}})])[0]

    resolved = pk.custom_metrics.resolve_by_name("Resolve By Name Test 1")
    assert resolved is not None
    assert resolved.name == "Resolve By Name Test 1"
    assert resolved.context == "patient"
    assert resolved.type == {"string": {}}

def test_resolve_by_name_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.CustomMetricLookupError) as err_wrapper:
        pk.custom_metrics.resolve("My Custom Metric")
    assert err_wrapper.value.message == "Custom metric with name `My Custom Metric` not found."

def test_update_custom_metrics(app, custom_metric_factory):
    pk = app.pk

    custom_metric = custom_metric_factory(("Update Me", "patient", {"string": {}}))[0]

    # Verify custom metric was updated successfully
    custom_metric.name = "Updated Custom Metric Name"
    custom_metric.context = "image_set"
    custom_metric.save()
    custom_metrics = pk.custom_metrics.query()
    for custom_metric in custom_metrics:
        if custom_metric.name == "Updated Custom Metric Name":
            custom_metric_match = custom_metric
            break
    else:
        custom_metric_match = None
    assert custom_metric_match is not None
    assert custom_metric_match.name == "Updated Custom Metric Name"
    assert custom_metric_match.context == "image_set"
    assert custom_metric_match.type == {"string": {}}

def test_update_custom_metrics_failure(app, custom_metric_factory):
    pk = app.pk

    custom_metric = custom_metric_factory([
        ("Update Me Failure", "patient", {"string": {}}),
        ("Duplicate Me 2", "patient", {"string": {}}),
    ])[0]

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        custom_metric.name = "Duplicate Me 2"
        custom_metric.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Custom metric already exists with name "Duplicate Me 2"'
