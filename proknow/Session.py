import six

from .Exceptions import WorkspaceLookupError


class Session(object):
    """

    This class should be used to interact with the current session. It is instantiated for you as
    an attribute of the :class:`proknow.ProKnow.ProKnow` class.

    """

    def __init__(self, proknow, requestor):
        """Initializes the Session class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor

    def get(self):
        """Gets the current user session.

        Returns:
            dict: A dictionary of user session attributes.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            Use this method to get the user session::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                session = pk.session.get()
                print(session["name"])
        """
        _, session = self._requestor.get('/user')
        return session
