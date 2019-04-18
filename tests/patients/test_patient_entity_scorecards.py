import pytest
import re

from proknow import Exceptions

def test_create(app, entity_generator, custom_metric_generator):
    pk = app.pk

    entity = entity_generator("./tests/data/Becker^Matthew", type="dose")
    _, custom_metric = custom_metric_generator()

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
        "id": custom_metric.id
    }])
    assert scorecard.name == "My Scorecard 2"
    assert len(scorecard.computed) == 2
    assert len(scorecard.custom) == 1

def test_create_failure(app, entity_generator):
    pk = app.pk

    entity = entity_generator("./tests/data/Becker^Matthew", type="dose")
    scorecard = entity.scorecards.create("My Scorecard", [], [])

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        entity.scorecards.create("My Scorecard", [], [])
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Entity metric set already exists with name "My Scorecard"'

def test_delete(app, entity_generator):
    pk = app.pk

    entity = entity_generator("./tests/data/Becker^Matthew", type="dose")
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

def test_delete_failure(app, entity_generator):
    pk = app.pk

    entity = entity_generator("./tests/data/Becker^Matthew", type="dose")
    scorecard = entity.scorecards.create("My Scorecard", [], [])
    scorecard.delete()

    # Assert error is raised when attempting to delete scorecard that does not exist
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        scorecard.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'Metric set "' + scorecard.id + '" not found in entity "' + entity.id + '"'

def test_find(app, entity_generator):
    pk = app.pk

    entity = entity_generator("./tests/data/Becker^Matthew", type="dose")
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

def test_query(app, entity_generator):
    pk = app.pk

    entity = entity_generator("./tests/data/Becker^Matthew", type="dose")
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

def test_update(app, entity_generator, custom_metric_generator):
    pk = app.pk

    entity = entity_generator("./tests/data/Becker^Matthew", type="dose")
    _, custom_metric = custom_metric_generator()
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
        "id": custom_metric.id
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

def test_update_failure(app, entity_generator):
    pk = app.pk

    entity = entity_generator("./tests/data/Becker^Matthew", type="dose")
    scorecard1 = entity.scorecards.create("My Scorecard 1", [], [])
    scorecard2 = entity.scorecards.create("My Scorecard 2", [], [])

    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        scorecard2.name = "My Scorecard 1"
        scorecard2.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'Entity metric set already exists with name "My Scorecard 1"'
