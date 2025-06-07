"""
Stub module for requests to satisfy imports in health_check without installing the package.
"""


class exceptions:
    class Timeout(Exception):
        """Timeout exception stub"""

        pass

    class ConnectionError(Exception):
        """ConnectionError exception stub"""

        pass


class Response:
    """Stub Response object"""

    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text

    def json(self):
        """Return stub JSON payload"""
        return {}


def get(url, headers=None, params=None, timeout=None):
    """Stub get method for health checks"""
    return Response()
