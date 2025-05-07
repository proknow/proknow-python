import json

def test_get_api_version(app, entity_generator, temp_directory):
    pk = app.pk

    api_version = pk.rtv.get_api_version()
    assert isinstance(api_version, str)
    api_version_dict = json.loads(api_version)
    assert "imageset" in api_version_dict
    assert "structureset" in api_version_dict
    assert "plan" in api_version_dict
    assert "dose" in api_version_dict

    api_version = pk.rtv.get_api_version("imageset")
    assert isinstance(api_version, str)
    api_version_dict = json.loads(api_version)
    assert "ct" in api_version_dict
    assert "mr" in api_version_dict
    assert "pt" in api_version_dict
