from __future__ import absolute_import

import json
import six

from .Auth import Auth
from .Requestor import Requestor
from .Workspaces import Workspaces
from .Roles import Roles
from .Users import Users


class ProKnow(object):
    """

    This is the main class that should be instatiated at the beginning of your Python program with
    your base URL (which should include your account subdomain) and your API token credentials.

    Attributes:
        requestor (:class:`proknow.Requestor.Requestor`): An instance of the Requestor class.
        workspaces (:class:`proknow.Workspaces.Workspaces`): An instance of the Workspaces class.
    """

    def __init__(self, base_url, credentials_file=None, credentials_id=None, credentials_secret=None):
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

        Raises:
            AssertionError: If the input parameters are invalid.
        """

        idValid = isinstance(credentials_id, six.string_types)
        tokenValid = isinstance(credentials_secret, six.string_types)
        fileValid = isinstance(credentials_file, six.string_types)

        assert isinstance(base_url, six.string_types), "`base_url` must be a string."
        assert (idValid and tokenValid) or fileValid, "`credentials_id`/`credentials_secret` or `credentials_file` are required as strings."
        if credentials_id is None or credentials_secret is None:
            with open(credentials_file, 'r') as file:
                data = json.load(file)
                assert "id" in data, "`credentials_file` does not contain id"
                assert "secret" in data, "`credentials_file` does not contain secret"
                credentials_id = data["id"]
                credentials_secret = data["secret"]

        self.requestor = Requestor(base_url, credentials_id, credentials_secret)
        
        self.workspaces = Workspaces(self, self.requestor)
        self.roles = Roles(self, self.requestor)
        self.users = Users(self, self.requestor)
