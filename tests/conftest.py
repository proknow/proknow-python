import pytest
import tempfile
import shutil

from pktestconfig import base_url, credentials_id, credentials_secret

from proknow import ProKnow

class App():
    def __init__(self):
        self.pk = ProKnow(base_url, credentials_id=credentials_id, credentials_secret=credentials_secret)
        self.marked_custom_metrics = []
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
                print('Error deleting role: ' + user.name)
                pass
        for workspace in self.marked_workspaces:
            try:
                if workspace.data["protected"] == True:
                    workspace.protected = False
                    workspace.save()
                workspace.delete()
            except:
                print('Error deleting workspace: ' + user.name)
                pass

@pytest.fixture(scope="module")
def app():
    proknow = App()
    yield proknow
    proknow.cleanup()

@pytest.fixture
def collection_factory(app):
    pk = app.pk

    def _create_collections(collections, do_not_mark=False):
        result = []
        if not isinstance(collections, list):
            collections = [collections]
        for custom_metric in collections:
            if isinstance(custom_metric, dict):
                created = pk.collections.create(**custom_metric)
            elif isinstance(custom_metric, tuple):
                created = pk.collections.create(*custom_metric)
            else:
                created = None
            result.append(created)
            if created is not None and do_not_mark is False:
                app.marked_collections.append(created)
        return result

    return _create_collections

@pytest.fixture
def custom_metric_factory(app):
    pk = app.pk

    def _create_custom_metrics(custom_metrics, do_not_mark=False):
        result = []
        if not isinstance(custom_metrics, list):
            custom_metrics = [custom_metrics]
        for custom_metric in custom_metrics:
            if isinstance(custom_metric, dict):
                created = pk.custom_metrics.create(**custom_metric)
            elif isinstance(custom_metric, tuple):
                created = pk.custom_metrics.create(*custom_metric)
            else:
                created = None
            result.append(created)
            if created is not None and do_not_mark is False:
                app.marked_custom_metrics.append(created)
        return result

    return _create_custom_metrics

@pytest.fixture
def workspace_factory(app):
    pk = app.pk

    def _create_workspaces(workspaces, do_not_mark=False):
        result = []
        if not isinstance(workspaces, list):
            workspaces = [workspaces]
        for workspace in workspaces:
            if isinstance(workspace, dict):
                created = pk.workspaces.create(**workspace)
            elif isinstance(workspace, tuple):
                created = pk.workspaces.create(*workspace)
            else:
                created = None
            result.append(created)
            if created is not None and do_not_mark is False:
                app.marked_workspaces.append(created)
        return result

    return _create_workspaces

@pytest.fixture
def role_factory(app):
    pk = app.pk

    def _create_roles(roles, do_not_mark=False):
        result = []
        if not isinstance(roles, list):
            roles = [roles]
        for role in roles:
            if isinstance(role, dict):
                created = pk.roles.create(**role)
            elif isinstance(role, tuple):
                created = pk.roles.create(*role)
            else:
                created = None
            result.append(created)
            if created is not None and do_not_mark is False:
                app.marked_roles.append(created)
        return result

    return _create_roles

@pytest.fixture
def user_factory(app):
    pk = app.pk

    def _create_users(users, do_not_mark=False):
        result = []
        if not isinstance(users, list):
            users = [users]
        for user in users:
            if isinstance(user, dict):
                created = pk.users.create(**user)
            elif isinstance(user, tuple):
                created = pk.users.create(*user)
            else:
                created = None
            result.append(created)
            if created is not None and do_not_mark is False:
                app.marked_users.append(created)
        return result

    return _create_users

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
