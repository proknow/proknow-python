__all__ = [
    'Requestor',
]

import requests
from requests.adapters import HTTPAdapter

from .Exceptions import HttpError


class Requestor(object):
    """A class used for issuing requests for the ProKnow API"""

    def __init__(self, base_url, username, password, max_retries=3):
        """Initializes the Requestor class.

        Parameters:
            base_url (str): The base URL to use when making request to the ProKnow API.
            username (str): The string used in Basic Authentication as the user name.
            password (str): The string used in Basic Authentication as the user password.
            max_retries (int, optional): The maximum number of for failed connection attempts.
        """
        self._username = username
        self._password = password
        self._base_url = base_url + "/api"
        self._session = requests.Session()
        self._session.mount('http', HTTPAdapter(max_retries=max_retries))
        self._session.mount('https', HTTPAdapter(max_retries=max_retries))

    def _handle_response(self, r, binary=False):
        if r.status_code >= 400:
            raise HttpError(r.status_code, r.text)
        if binary == True:
            return (r, r.content)
        try:
            return (r, r.json())
        except ValueError:
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
        r = self._session.get(self._base_url + route, auth=(self._username, self._password), **kwargs)
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
        r = self._session.get(self._base_url + route, auth=(self._username, self._password), **kwargs)
        return self._handle_response(r, True)

    def delete(self, route, **kwargs):
        """Issues an HTTP ``DELETE`` request.

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
        r = self._session.delete(self._base_url + route, auth=(self._username, self._password), **kwargs)
        return self._handle_response(r)

    def patch(self, route, **kwargs): # pragma: no cover (not used right now)
        """Issues an HTTP ``PATCH`` request.

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
        r = self._session.patch(self._base_url + route, auth=(self._username, self._password), **kwargs)
        return self._handle_response(r)

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
        r = self._session.post(self._base_url + route, auth=(self._username, self._password), **kwargs)
        return self._handle_response(r)

    def put(self, route, **kwargs):
        """Issues an HTTP ``PUT`` request.

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
        r = self._session.put(self._base_url + route, auth=(self._username, self._password), **kwargs)
        return self._handle_response(r)

    def stream(self, route, path):
        """Issues an HTTP ``PUT`` request.

        Parameters:
            route (str): The API route to use in the request.
            path (str): The file path to stream the request response.
        """
        with open(path, 'wb') as file:
            with self._session.get(self._base_url + route, auth=(self._username, self._password), stream=True) as r:
                if r.status_code >= 400: # pragma: no cover (difficult to hit)
                    raise HttpError(r.status_code, r.text)
                for chunk in r.iter_content(chunk_size=5242880):
                    if chunk:
                        file.write(chunk)
                    else: # pragma: no cover (included for completeness)
                        pass
