"""
openlp/core/api/endpoint.py: Endpoint stuff
"""


class Endpoint(object):
    """
    This is an endpoint for the API
    """
    def __init__(self, url_prefix):
        """
        Create an endpoint with a URL prefix
        """
        print("init")
        self.url_prefix = url_prefix
        self.routes = []

    def add_url_route(self, url, view_func, method, secure):
        """
        Add a url route to the list of routes
        """
        self.routes.append((url, view_func, method, secure))

    def route(self, rule, method='GET', secure=False):
        """
        Set up a URL route
        """
        def decorator(func):
            """
            Make this a decorator
            """
            self.add_url_route(rule, func, method, secure)
            return func
        return decorator
