__all__ = [
    'RtvRequestor',
]

import requests
import re
from requests.adapters import HTTPAdapter

from .Exceptions import HttpError


class RtvRequestor(object):
    """A class used for issuing requests for the RT Visualizer API"""

    def __init__(self, base_url, username, password, max_retries=3):
        """Initializes the RtvRequestor class.

        Parameters:
            base_url (str): The base URL to use when making request to the ProKnow API.
            username (str): The string used in Basic Authentication as the user name.
            password (str): The string used in Basic Authentication as the user password.
            max_retries (int, optional): The maximum number of for failed connection attempts.
        """
        self._username = username
        self._password = password
        self._base_url = base_url
        self._source = None
        self._session = requests.Session()
        self._session.mount('http', HTTPAdapter(max_retries=max_retries))
        self._session.mount('https', HTTPAdapter(max_retries=max_retries))
    
    def _get_prefix(self):
        if self._source is None:
            r = self._session.get(self._base_url + "/ui/variables.js", auth=(self._username, self._password))
            match = re.search(r'"rtVisualizerSourceName":"([\w-]+)"', r.text)
            self._source = match.group(1)
        return self._base_url + "/rtv/" + self._source

    def _handle_response(self, r, binary=False):
        if r.status_code >= 400:
            raise HttpError(r.status_code, r.text)
        if binary == True:
            return (r, r.content)
        try:
            return (r, r.json())
        except ValueError: # pragma: no cover (included for consistency)
            return (r, r.text)

    def get(self, route, **kwargs):
        """Issues an HTTP ``GET`` request.

        Parameters:
            route (str): The API route to use in the request.
            **kwargs (dict, optional): Additional keyword arguments to pass through in the
                request.

        Returns:
            tuple: A tuple (res, msg).

            1. res (Response): the Response object
            2. msg (str, dict): the text response or, if the response was JSON, the decoded JSON
               dictionary.
        """
        prefix = self._get_prefix()
        r = self._session.get(prefix + route, **kwargs)
        return self._handle_response(r)

    def get_binary(self, route, **kwargs):
        """Issues an HTTP ``GET`` request, returning the binary data.

        This method is useful when the response is known to not be JSON encoded and should be
        returned instead as a string of bytes.

        Parameters:
            route (str): The API route to use in the request.
            **kwargs (dict, optional): Additional keyword arguments to pass through in the
                request.

        Returns:
            tuple: A tuple (res, data).

            1. res (Response): the Response object
            2. data (bytes): The resonse as a byte string
        """
        prefix = self._get_prefix()
        r = self._session.get(prefix + route, **kwargs)
        return self._handle_response(r, True)

    def post(self, route, **kwargs):
        """Issues an HTTP ``POST`` request.

        Parameters:
            route (str): The API route to use in the request.
            **kwargs (dict, optional): Additional keyword arguments to pass through in the
                request.

        Returns:
            tuple: A tuple (res, msg).

            1. res (Response): the Response object
            2. msg (str, dict): the text response or, if the response was JSON, the decoded JSON
               dictionary.
        """
        prefix = self._get_prefix()
        r = self._session.post(prefix + route, **kwargs)
        return self._handle_response(r)
