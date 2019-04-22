__all__ = [
    'Requestor',
]

import requests

from .Exceptions import HttpError


class Requestor(object):
    """A class used for issuing requests for the ProKnow API"""

    def __init__(self, base_url, username, password):
        """Initializes the Requestor class.

        Parameters:
            base_url (str): The base URL to use when making request to the ProKnow API.
            username (str): The string used in Basic Authentication as the user name.
            password (str): The string used in Basic Authentication as the user password.
        """
        self._username = username
        self._password = password
        self._base_url = base_url + "/api"

    def _handle_response(self, r):
        if r.status_code >= 400:
            raise HttpError(r.status_code, r.text)
        try:
            return (r.status_code, r.json())
        except ValueError:
            return (r.status_code, r.text)

    def get_auth(self):
        return (self._username, self._password)

    def get_base_url(self):
        return self._base_url

    def get(self, route, query=None, headers=None):
        """Issues an HTTP ``GET`` request.

        Parameters:
            route (str): The API route to use in the request.
            query (dict, optional): An optional dictionary of query parameters to use in the
                request.
            headers (dict, optional): An optional dictionary of request headers to use in the
                request.

        Returns:
            tuple: A tuple (status_code, msg).

            1. status_code (int): the response code
            2. msg (str, dict): the text response or, if the response was JSON, the decoded JSON
               dictionary.
        """
        r = requests.get(self._base_url + route, params=query, headers=headers, auth=(self._username, self._password))
        return self._handle_response(r)

    def delete(self, route, query=None, body=None, headers=None):
        """Issues an HTTP ``DELETE`` request.

        Parameters:
            route (str): The API route to use in the request.
            query (dict, optional): An optional dictionary of query parameters to use in the
                request.
            body (dict, optional): An optional dictionary to be used as a JSON request body for the
                request.
            headers (dict, optional): An optional dictionary of request headers to use in the
                request.

        Returns:
            tuple: A tuple (status_code, msg).

            1. status_code (int): the response code
            2. msg (str, dict): the text response or, if the response was JSON, the decoded JSON
               dictionary.
        """
        r = requests.delete(self._base_url + route, params=query, headers=headers, auth=(self._username, self._password), json=body)
        return self._handle_response(r)

    def patch(self, route, query=None, body=None, headers=None):
        """Issues an HTTP ``PATCH`` request.

        Parameters:
            route (str): The API route to use in the request.
            query (dict, optional): An optional dictionary of query parameters to use in the
                request.
            body (dict, optional): An optional dictionary to be used as a JSON request body for the
                request.
            headers (dict, optional): An optional dictionary of request headers to use in the
                request.

        Returns:
            tuple: A tuple (status_code, msg).

            1. status_code (int): the response code
            2. msg (str, dict): the text response or, if the response was JSON, the decoded JSON
               dictionary.
        """
        r = requests.patch(self._base_url + route, params=query, headers=headers, auth=(self._username, self._password), json=body)
        return self._handle_response(r)

    def post(self, route, query=None, body=None, headers=None):
        """Issues an HTTP ``POST`` request.

        Parameters:
            route (str): The API route to use in the request.
            query (dict, optional): An optional dictionary of query parameters to use in the
                request.
            body (dict, optional): An optional dictionary to be used as a JSON request body for the
                request.
            headers (dict, optional): An optional dictionary of request headers to use in the
                request.

        Returns:
            tuple: A tuple (status_code, msg).

            1. status_code (int): the response code
            2. msg (str, dict): the text response or, if the response was JSON, the decoded JSON
               dictionary.
        """
        r = requests.post(self._base_url + route, params=query, headers=headers, auth=(self._username, self._password), json=body)
        return self._handle_response(r)

    def put(self, route, query=None, body=None, headers=None):
        """Issues an HTTP ``PUT`` request.

        Parameters:
            route (str): The API route to use in the request.
            query (dict, optional): An optional dictionary of query parameters to use in the
                request.
            body (dict, optional): An optional dictionary to be used as a JSON request body for the
                request.
            headers (dict, optional): An optional dictionary of request headers to use in the
                request.

        Returns:
            tuple: A tuple (status_code, msg).

            1. status_code (int): the response code
            2. msg (str, dict): the text response or, if the response was JSON, the decoded JSON
               dictionary.
        """
        r = requests.put(self._base_url + route, params=query, headers=headers, auth=(self._username, self._password), json=body)
        return self._handle_response(r)

    def stream(self, route, path):
        """Issues an HTTP ``PUT`` request.

        Parameters:
            route (str): The API route to use in the request.
            path (str): The file path to stream the request response
            query (dict, optional): An optional dictionary of query parameters to use in the
                request.
            body (dict, optional): An optional dictionary to be used as a JSON request body for the
                request.
        """
        with open(path, 'wb') as file:
            with requests.get(self._base_url + route, auth=(self._username, self._password), stream=True) as r:
                if r.status_code >= 400:
                    raise HttpError(r.status_code, r.text)
                for chunk in r.iter_content(chunk_size=5242880):
                    if chunk:
                        file.write(chunk)
