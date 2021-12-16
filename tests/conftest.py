import pytest
import tempfile
import shutil
import string
import random

from pktestconfig import base_url, credentials_id, credentials_secret

from proknow import ProKnow

class App():
    def __init__(self):
        self.pk = ProKnow(base_url, credentials_id=credentials_id, credentials_secret=credentials_secret)
        self.resource_prefix = "pkpy"
        self.marked_custom_metrics = []
        self.marked_scorecard_templates = []
        self.marked_workspaces = []
        self.marked_roles = []
        self.marked_users = []
        self.marked_collections = []

    def cleanup(self):
        for collection in self.marked_collections:
            try:
                collection.delete()
            except:
                print('Error deleting collection: ' + collection.name)
                pass
        for custom_metric in self.marked_custom_metrics:
            try:
                custom_metric.delete()
            except:
                print('Error deleting custom metric: ' + custom_metric.name)
                pass
        for scorecard_template in self.marked_scorecard_templates:
            try:
                scorecard_template.delete()
            except:
                print('Error deleting scorecard template: ' + scorecard_template.name)
                pass
        for user in self.marked_users:
            try:
                user.delete()
            except:
                print('Error deleting user: ' + user.name)
                pass
        for role in self.marked_roles:
            try:
                role.delete()
            except:
                print('Error deleting role: ' + role.name)
                pass
        for workspace in self.marked_workspaces:
            try:
                if workspace.data["protected"] == True:
                    workspace.protected = False
                    workspace.save()
                workspace.delete()
            except:
                print('Error deleting workspace: ' + workspace.name)
                pass

def generate_string(size=10, lowercase_only=False):
    if lowercase_only:
        characters = string.ascii_lowercase + string.digits
    else:
        characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(size))

@pytest.fixture(scope="module")
def app():
    proknow = App()
    yield proknow
    proknow.cleanup()

@pytest.fixture
def collection_generator(app):
    pk = app.pk
    resource_prefix = app.resource_prefix

    def _create_collection(do_not_mark=False, **args):
        params = {
            "name": resource_prefix + generate_string(),
            "description": generate_string(),
            "type": "organization",
            "workspaces": []
        }
        params.update(args)
        if params["name"].find(resource_prefix) != 0:
            params["name"] = resource_prefix + params["name"]
        collection = pk.collections.create(**params)
        if do_not_mark is False:
            app.marked_users.append(collection)
        return (params, collection)

    return _create_collection

@pytest.fixture
def custom_metric_generator(app):
    pk = app.pk
    resource_prefix = app.resource_prefix

    def _create_custom_metric(do_not_mark=False, **args):
        params = {
            "name": resource_prefix + generate_string(),
            "context": "patient",
            "type": {
                "number": {}
            }
        }
        params.update(args)
        if params["name"].find(resource_prefix) != 0:
            params["name"] = resource_prefix + params["name"]
        custom_metric = pk.custom_metrics.create(**params)
        if do_not_mark is False:
            app.marked_custom_metrics.append(custom_metric)
        return (params, custom_metric)

    return _create_custom_metric

@pytest.fixture
def scorecard_template_generator(app):
    pk = app.pk
    resource_prefix = app.resource_prefix

    def _create_scorecard_template(do_not_mark=False, **args):
        params = {
            "name": resource_prefix + generate_string(),
            "computed": [],
            "custom": []
        }
        params.update(args)
        if params["name"].find(resource_prefix) != 0:
            params["name"] = resource_prefix + params["name"]
        scorecard_template = pk.scorecard_templates.create(**params)
        if do_not_mark is False:
            app.marked_scorecard_templates.append(scorecard_template)
        return (params, scorecard_template)

    return _create_scorecard_template

@pytest.fixture
def entity_generator(app, workspace_generator):
    pk = app.pk

    def _create_entity(path_or_paths, **args):
        _, workspace = workspace_generator()
        batch = pk.uploads.upload(workspace.id, path_or_paths)
        length = len(batch.patients)
        assert length == 1, "entity_generator: only 1 patient at a time supported; got " + length
        if len(args) > 0:
            entities = batch.patients[0].get().find_entities(**args)
            length = len(entities)
            assert length == 1, "entity_generator: only 1 entity at a time supported; got " + length
            return entities[0].get()
        else:
            length = len(batch.patients[0].entities)
            assert length == 1, "entity_generator: only 1 entity at a time supported; got " + length
            return batch.patients[0].entities[0].get()

    return _create_entity

@pytest.fixture
def patient_generator(app, workspace_generator):
    pk = app.pk

    def _create_patient(path_or_paths):
        _, workspace = workspace_generator()
        batch = pk.uploads.upload(workspace.id, path_or_paths)
        length = len(batch.patients)
        assert length == 1, "patient_generator: only 1 patient at a time supported; got " + length
        return batch.patients[0].get()

    return _create_patient

@pytest.fixture
def role_generator(app):
    pk = app.pk
    resource_prefix = app.resource_prefix

    def _create_role(do_not_mark=False, **args):
        params = {
            "name": resource_prefix + generate_string(),
            "permissions": {
                "create_api_keys": False,
                "manage_access": False,
                "manage_custom_metrics": False,
                "manage_template_metric_sets": False,
                "manage_renaming_rules": False,
                "manage_template_checklists": False,
                "manage_audit_logs": False,
                "manage_template_structure_sets": False,
                "manage_workspace_algorithms": False,
                "organization_manage_access_patients": False,
                "organization_collaborator": False,
                "organization_read_patients": False,
                "organization_read_collections": False,
                "organization_view_phi": False,
                "organization_download_dicom": False,
                "organization_upload_dicom": False,
                "organization_write_collections": False,
                "organization_write_patients": False,
                "organization_contour_patients": False,
                "organization_delete_collections": False,
                "organization_delete_patients": False,
                "workspaces": [],
            }
        }
        params.update(args)
        if params["name"].find(resource_prefix) != 0:
            params["name"] = resource_prefix + params["name"]
        role = pk.roles.create(**params)
        if do_not_mark is False:
            app.marked_roles.append(role)
        return (params, role)

    return _create_role

class TempDirectory(object):
    def __init__(self):
        self.path = tempfile.mkdtemp()

    def cleanup(self):
        shutil.rmtree(self.path)

@pytest.fixture
def temp_directory():
    temp = TempDirectory()
    yield temp
    temp.cleanup()

@pytest.fixture
def user_generator(app):
    pk = app.pk
    resource_prefix = app.resource_prefix

    def _create_user(do_not_mark=False, **args):
        params = {
            "email": resource_prefix + generate_string(lowercase_only=True) + '@proknow.com',
            "name": generate_string(),
            "role_id": pk.roles.find(name="Admin").id
        }
        params.update(args)
        if params["email"].find(resource_prefix) != 0:
            params["email"] = resource_prefix + params["email"]
        user = pk.users.create(**params)
        if do_not_mark is False:
            app.marked_users.append(user)
        return (params, user)

    return _create_user

@pytest.fixture
def workspace_generator(app):
    pk = app.pk
    resource_prefix = app.resource_prefix

    def _create_workspace(do_not_mark=False, **args):
        params = {
            "slug": resource_prefix + generate_string(lowercase_only=True),
            "name": generate_string(),
            "protected": False
        }
        params.update(args)
        if params["slug"].find(resource_prefix) != 0:
            params["slug"] = resource_prefix + params["slug"]
        workspace = pk.workspaces.create(**params)
        if do_not_mark is False:
            app.marked_workspaces.append(workspace)
        return (params, workspace)

    return _create_workspace
