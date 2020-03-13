from __future__ import absolute_import

import json
import six

from .Requestor import Requestor
from .Session import Session
from .CustomMetrics import CustomMetrics
from .ScorecardTemplates import ScorecardTemplates
from .Workspaces import Workspaces
from .Roles import Roles
from .Users import Users
from .Uploads import Uploads
from .Patients import Patients
from .Collections import Collections


class ProKnow(object):
    """

    This is the main class that should be instatiated at the beginning of your Python program with
    your base URL (which should include your account subdomain) and your API token credentials.

    Attributes:
        requestor (:class:`proknow.Requestor.Requestor`): An instance of the Requestor class.
        session (:class:`proknow.Session.Session`): An instance of the Session class.
        custom_metrics (:class:`ProKnow.CustomMetrics.CustomMetrics`): An instance of the
            CustomMetrics class.
        scorecard_templates (:class:`ProKnow.ScorecardTemplates.ScorecardTemplates`): An instance
            of the ScorecardTemplates class.
        workspaces (:class:`proknow.Workspaces.Workspaces`): An instance of the Workspaces class.
        roles (:class:`proknow.Roles.Roles`): An instance of the Roles class.
        users (:class:`proknow.Users.Users`): An instance of the Users class.
        uploads (:class:`proknow.Uploads.Uploads`): An instance of the Uploads class.
        patients (:class:`proknow.Patients.Patients`): An instance of the Patients class.
        collections (:class:`proknow.Collections.Collections`): An instance of the Collections
            class.
        LOCK_RENEWAL_BUFFER (int): The number of seconds to use as a buffer when renewing a lock for
            a draft structure set.
        ENTITY_WAIT_TIMEOUT (int): The number of seconds to wait for plan delivery information and
            dose analysis data to be ready.
    """

    def __init__(self, base_url, credentials_file=None, credentials_id=None, credentials_secret=None,
        LOCK_RENEWAL_BUFFER=30, ENTITY_WAIT_TIMEOUT=10):
        """Initializes the ProKnow class.

        The `base_url` must be provided as should either the `credentials_file` or both the
        `credentials_id` and `credentials_secret`.

        Parameters:
            base_url (str): The base URL to use when making request to the ProKnow API.
            credentials_file (str): The path to the credentials file obtained by creating an API
                key in your ProKnow account. The file should be a JSON file containing an object
                with the fields `id` and `secret`.
            credentials_id (str): An API key id.
            credentials_secret (str): An API key secret.
            LOCK_RENEWAL_BUFFER (int, optional): The number of seconds to use as a buffer when
                renewing a lock for a draft structure set. As an example, the default value of 30
                means that the renewer will attempt to renew the lock 30 seconds before it actually
                expires.
            ENTITY_WAIT_TIMEOUT (int, optional): The number of seconds to wait for plan delivery
                information and dose analysis data to be ready.

        Raises:
            AssertionError: If the input parameters are invalid.
        """

        idValid = isinstance(credentials_id, six.string_types)
        tokenValid = isinstance(credentials_secret, six.string_types)
        fileValid = isinstance(credentials_file, six.string_types)

        assert isinstance(base_url, six.string_types), "`base_url` must be a string."
        assert (idValid and tokenValid) or fileValid, "`credentials_id`/`credentials_secret` or `credentials_file` are required as strings."
        if credentials_id is None or credentials_secret is None: # pragma: no cover (not testing with file in unit tests)
            with open(credentials_file, 'r') as file:
                data = json.load(file)
                assert "id" in data, "`credentials_file` does not contain id"
                assert "secret" in data, "`credentials_file` does not contain secret"
                credentials_id = data["id"]
                credentials_secret = data["secret"]

        self.LOCK_RENEWAL_BUFFER = LOCK_RENEWAL_BUFFER
        self.ENTITY_WAIT_TIMEOUT = ENTITY_WAIT_TIMEOUT

        self.requestor = Requestor(base_url, credentials_id, credentials_secret)

        self.session = Session(self, self.requestor)
        self.custom_metrics = CustomMetrics(self, self.requestor)
        self.scorecard_templates = ScorecardTemplates(self, self.requestor)
        
        self.workspaces = Workspaces(self, self.requestor)
        self.roles = Roles(self, self.requestor)
        self.users = Users(self, self.requestor)

        self.uploads = Uploads(self, self.requestor)

        self.patients = Patients(self, self.requestor)
        self.collections = Collections(self, self.requestor)
