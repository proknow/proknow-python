import pytest
import re
import six

from proknow import Exceptions

def test_create(app, custom_metric_generator, scorecard_template_generator):
    pk = app.pk

    _, custom_metric = custom_metric_generator()

    # Verify returned ScorecardTemplateItem
    params, scorecard_template = scorecard_template_generator()
    assert scorecard_template.name == params["name"]
    assert scorecard_template.computed == params["computed"]
    assert scorecard_template.custom == params["custom"]
    assert isinstance(scorecard_template.data, dict)

    # Assert item can be found in query
    scorecard_templates = pk.scorecard_templates.query()
    for scorecard_template in scorecard_templates:
        if scorecard_template.name == params["name"]:
            scorecard_template_match = scorecard_template
            break
    else:
        scorecard_template_match = None
    assert scorecard_template_match is not None

    computed = [{
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
    custom = [{
        "id": custom_metric.id
    }]
    params, scorecard_template = scorecard_template_generator(computed=computed, custom=custom)
    assert scorecard_template.name == params["name"]
    assert scorecard_template.computed == params["computed"]
    assert scorecard_template.custom == params["custom"]

def test_create_failure(app, scorecard_template_generator):
    pk = app.pk

    params, scorecard_template = scorecard_template_generator()

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.scorecard_templates.create(**params)
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Metric template already exists with name "' + params["name"] + '"'

def test_delete(app, scorecard_template_generator):
    pk = app.pk

    params, scorecard_template = scorecard_template_generator(do_not_mark=True)

    # Verify scorecard template was deleted successfully
    scorecard_template.delete()
    for scorecard_template in pk.scorecard_templates.query():
        if scorecard_template.name == params["name"]:
            match = scorecard_template
            break
    else:
        match = None
    assert match is None

def test_delete_failure(app, scorecard_template_generator):
    pk = app.pk

    params, scorecard_template = scorecard_template_generator(do_not_mark=True)

    scorecard_template.delete()
    # Assert error is raised when attempting to delete protected custom metric
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        scorecard_template.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'Metric template "' + scorecard_template.id + '" not found'

def test_find(app, scorecard_template_generator):
    pk = app.pk

    params, scorecard_template = scorecard_template_generator(name="Find Me")
    expr = re.compile(r"ind M")

    # Find with no args
    found = pk.scorecard_templates.find()
    assert found is None

    # Find using predicate
    found = pk.scorecard_templates.find(lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is not None

    # Find using props
    found = pk.scorecard_templates.find(id=scorecard_template.id, name=params["name"])
    assert found is not None

    # Find using both
    found = pk.scorecard_templates.find(lambda ws: expr.search(ws.data["name"]) is not None, id=scorecard_template.id, name=params["name"])
    assert found is not None

    # Find failure
    found = pk.scorecard_templates.find(lambda ws: expr.search(ws.data["id"]) is not None)
    assert found is None
    found = pk.scorecard_templates.find(id=scorecard_template.id, name=params["name"].lower())
    assert found is None

def test_query(app, scorecard_template_generator):
    pk = app.pk

    params1, scorecard_template1 = scorecard_template_generator()
    params2, scorecard_template2 = scorecard_template_generator()

    # Verify test 1
    for scorecard_template in pk.scorecard_templates.query():
        if scorecard_template.name == params1["name"]:
            match = scorecard_template
            break
    else:
        match = None
    assert match is not None
    assert isinstance(match.id, six.string_types)
    assert match.name == params1["name"]

    # Verify test 2
    for scorecard_template in pk.scorecard_templates.query():
        if scorecard_template.name == params2["name"]:
            match = scorecard_template
            break
    else:
        match = None
    assert match is not None
    assert isinstance(match.id, six.string_types)
    assert match.name == params2["name"]

def test_resolve(app, scorecard_template_generator):
    pk = app.pk

    params, scorecard_template = scorecard_template_generator()

    # Test resolve by id
    resolved = pk.scorecard_templates.resolve(scorecard_template.id)
    assert resolved is not None
    assert resolved.name == params["name"]

    # Test resolve by name
    resolved = pk.scorecard_templates.resolve(params["name"])
    assert resolved is not None
    assert resolved.name == params["name"]

def test_resolve_failure(app):
    pk = app.pk

    # Test resolve by id
    with pytest.raises(Exceptions.ScorecardTemplateLookupError) as err_wrapper:
        pk.scorecard_templates.resolve("00000000000000000000000000000000")
    assert err_wrapper.value.message == "Scorecard template with id `00000000000000000000000000000000` not found."

    # Test resolve by name
    with pytest.raises(Exceptions.ScorecardTemplateLookupError) as err_wrapper:
        pk.scorecard_templates.resolve("My Scorecard")
    assert err_wrapper.value.message == "Scorecard template with name `My Scorecard` not found."

def test_resolve_by_id(app, scorecard_template_generator):
    pk = app.pk

    params, scorecard_template = scorecard_template_generator()

    resolved = pk.scorecard_templates.resolve_by_id(scorecard_template.id)
    assert resolved is not None
    assert resolved.name == params["name"]

def test_resolve_by_id_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.ScorecardTemplateLookupError) as err_wrapper:
        pk.scorecard_templates.resolve_by_id("00000000000000000000000000000000")
    assert err_wrapper.value.message == "Scorecard template with id `00000000000000000000000000000000` not found."

def test_resolve_by_name(app, scorecard_template_generator):
    pk = app.pk

    params, scorecard_template = scorecard_template_generator(name="template-lower1")

    resolved = pk.scorecard_templates.resolve_by_name(params["name"])
    assert resolved is not None
    assert resolved.name == params["name"]

    resolved = pk.scorecard_templates.resolve_by_name(params["name"].upper())
    assert resolved is not None
    assert resolved.name == params["name"]

def test_resolve_by_name_failure(app):
    pk = app.pk

    with pytest.raises(Exceptions.ScorecardTemplateLookupError) as err_wrapper:
        pk.scorecard_templates.resolve("My Scorecard")
    assert err_wrapper.value.message == "Scorecard template with name `My Scorecard` not found."

def test_update(app, custom_metric_generator, scorecard_template_generator):
    pk = app.pk

    _, custom_metric = custom_metric_generator()
    _, scorecard = scorecard_template_generator(name="My Scorecard")

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
        "id": custom_metric.id
    }]
    scorecard.save()
    scorecards = pk.scorecard_templates.query()
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

def test_update_failure(app, scorecard_template_generator):
    pk = app.pk

    params, _ = scorecard_template_generator()
    _, scorecard = scorecard_template_generator()

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        scorecard.name = params["name"]
        scorecard.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Metric template already exists with name "' + params["name"] + '"'
