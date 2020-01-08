import pytest
import re

from proknow import Exceptions

def test_create(app, custom_metric_generator):
    pk = app.pk

    # Verify returned CustomMetricItem
    params, custom_metric = custom_metric_generator()
    assert custom_metric.name == params["name"]
    assert custom_metric.context == params["context"]
    assert custom_metric.type == params["type"]

    # Assert item can be found in query
    custom_metrics = pk.custom_metrics.query()
    for custom_metric in custom_metrics:
        if custom_metric.name == params["name"]:
            custom_metric_match = custom_metric
            break
    else:
        custom_metric_match = None
    assert custom_metric_match is not None
    assert custom_metric_match.name == params["name"]
    assert custom_metric_match.context == params["context"]
    assert custom_metric_match.type == params["type"]

def test_create_failure(app, custom_metric_generator):
    pk = app.pk

    params, custom_metric = custom_metric_generator()

    # Assert error is raised for duplicate custom metric
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.custom_metrics.create(**params)
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Custom metric already exists with name "' + params["name"] + '"'

def test_delete(app, custom_metric_generator):
    pk = app.pk

    params, custom_metric = custom_metric_generator(do_not_mark=True)

    # Verify custom metric was deleted successfully
    custom_metric.delete()
    for custom_metric in pk.custom_metrics.query():
        if custom_metric.name == params["name"]:
            match = custom_metric
            break
    else:
        match = None
    assert match is None

def test_delete_failure(app, custom_metric_generator):
    pk = app.pk

    params, custom_metric = custom_metric_generator(do_not_mark=True)

    custom_metric.delete()
    # Assert error is raised when attempting to delete protected custom metric
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        custom_metric.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'Custom metric "' + custom_metric.id + '" not found'

def test_find(app, custom_metric_generator):
    pk = app.pk

    params, custom_metric = custom_metric_generator(name="Find Me")
    expr = re.compile(r"ind M")

    # Find with no args
    found = pk.custom_metrics.find()
    assert found is None

    # Find using predicate
    found = pk.custom_metrics.find(lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is not None
    assert found.name == params["name"]
    assert found.context == params["context"]
    assert found.type == params["type"]

    # Find using props
    found = pk.custom_metrics.find(id=custom_metric.id, name=params["name"])
    assert found is not None
    assert found.name == params["name"]
    assert found.context == params["context"]
    assert found.type == params["type"]

    # Find using both
    found = pk.custom_metrics.find(lambda ws: expr.search(ws.data["name"]) is not None, id=custom_metric.id, name=params["name"])
    assert found is not None
    assert found.name == params["name"]
    assert found.context == params["context"]
    assert found.type == params["type"]

    # Find failure
    found = pk.custom_metrics.find(lambda ws: expr.search(ws.data["id"]) is not None)
    assert found is None
    found = pk.custom_metrics.find(id=custom_metric.id, name=params["name"].lower())
    assert found is None

def test_query(app, custom_metric_generator):
    pk = app.pk

    params1, custom_metric1 = custom_metric_generator()
    params2, custom_metric2 = custom_metric_generator()

    # Verify test 1
    for custom_metric in pk.custom_metrics.query():
        if custom_metric.name == params1["name"]:
            match = custom_metric
            break
    else:
        match = None
    assert match is not None
    assert match.name == params1["name"]
    assert match.context == params1["context"]
    assert match.type == params1["type"]

    # Verify test 2
    for custom_metric in pk.custom_metrics.query():
        if custom_metric.name == params2["name"]:
            match = custom_metric
            break
    else:
        match = None
    assert match is not None
    assert match.name == params2["name"]
    assert match.context == params2["context"]
    assert match.type == params2["type"]

def test_resolve(app, custom_metric_generator):
    pk = app.pk

    params, custom_metric = custom_metric_generator()

    # Test resolve by id
    resolved = pk.custom_metrics.resolve(custom_metric.id)
    assert resolved is not None
    assert resolved.name == params["name"]
    assert resolved.context == params["context"]
    assert resolved.type == params["type"]

    # Test resolve by name
    resolved = pk.custom_metrics.resolve(params["name"])
    assert resolved is not None
    assert resolved.name == params["name"]
    assert resolved.context == params["context"]
    assert resolved.type == params["type"]

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

def test_resolve_by_id(app, custom_metric_generator):
    pk = app.pk

    params, custom_metric = custom_metric_generator()

    resolved = pk.custom_metrics.resolve_by_id(custom_metric.id)
    assert resolved is not None
    assert resolved.name == params["name"]
    assert resolved.context == params["context"]
    assert resolved.type == params["type"]

def test_resolve_by_id_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.CustomMetricLookupError) as err_wrapper:
        pk.custom_metrics.resolve_by_id("00000000000000000000000000000000")
    assert err_wrapper.value.message == "Custom metric with id `00000000000000000000000000000000` not found."

def test_resolve_by_name(app, custom_metric_generator):
    pk = app.pk

    params, custom_metric = custom_metric_generator(name="custom-lower1")

    resolved = pk.custom_metrics.resolve_by_name(params["name"])
    assert resolved is not None
    assert resolved.name == params["name"]
    assert resolved.context == params["context"]
    assert resolved.type == params["type"]

    resolved = pk.custom_metrics.resolve_by_name(params["name"].upper())
    assert resolved is not None
    assert resolved.name == params["name"]
    assert resolved.context == params["context"]
    assert resolved.type == params["type"]

def test_resolve_by_name_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.CustomMetricLookupError) as err_wrapper:
        pk.custom_metrics.resolve("My Custom Metric")
    assert err_wrapper.value.message == "Custom metric with name `My Custom Metric` not found."

def test_update(app, custom_metric_generator):
    pk = app.pk
    resource_prefix = app.resource_prefix

    params, custom_metric = custom_metric_generator()

    # Verify custom metric was updated successfully
    updated_name = resource_prefix + "Updated Custom Metric Name"
    custom_metric.name = updated_name
    custom_metric.context = "image_set"
    custom_metric.save()
    custom_metrics = pk.custom_metrics.query()
    for custom_metric in custom_metrics:
        if custom_metric.name == updated_name:
            custom_metric_match = custom_metric
            break
    else:
        custom_metric_match = None
    assert custom_metric_match is not None
    assert custom_metric_match.name == updated_name
    assert custom_metric_match.context == "image_set"
    assert custom_metric_match.type == params["type"]

def test_update_failure(app, custom_metric_generator):
    pk = app.pk

    params1, _ = custom_metric_generator()
    params2, custom_metric = custom_metric_generator()

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        custom_metric.name = params1["name"]
        custom_metric.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Custom metric already exists with name "' + params1["name"] + '"'
