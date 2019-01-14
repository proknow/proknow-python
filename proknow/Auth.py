
class Auth(object):
    """A class used for storing authentication keys and generating appropriate Authorization headers"""

    def __init__(self, credentials_id, credentials_secret):
        self.username = credentials_id
        self.password = credentials_secret
