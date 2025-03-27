import os
import os.path
import webbrowser
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from wsgiref import simple_server

from google_auth_oauthlib.flow import _RedirectWSGIApp

from asset_core.configs import Configs
from asset_core.server.base_server import BaseServer


class AuthServer(BaseServer):

    def __init__(self):
        self.configs = Configs.shared().auth

    def _auth_url_route(self):
        return os.path.join(self.url, self.configs.auth_url_route)

    def _response_login_route(self):
        return os.path.join(self.url, self.configs.response_login_route)

    def _token_login_route(self):
        return os.path.join(self.url, self.configs.token_login_route)

    def _signup_route(self):
        return os.path.join(self.url, self.configs.user_signup_route)

    def get_auth_url(self):
        return self.parse(self.get(url=self._auth_url_route()))

    def login_with_response(self, data: dict) -> dict:
        return self.parse(self.post(url=self._response_login_route(), data=data))

    def login_with_token(self, token: str) -> dict:
        return self.parse(self.post(url=self._token_login_route(), data={"token": token}))

    def signup_user(self, username: str, email: str):
        return self.parse(self.post(url=self._signup_route(), data={"username": username, "email": email}))

    def google_oauth(self):
        """Authenticate the user bases on authorization response.

        Use auth_url instead of config to verify the user.
        Open the auth_url in the browser and get the auth_response.
        Verify the auth_response with the asset_server and get user info.
        """
        auth_url = self.get_auth_url()
        response_data = self.google_auth_response(auth_url)
        user_data = self.login_with_response(data=response_data)
        return user_data

    def google_auth_response(self, auth_url):
        """Open the auth_url in the browser and get the auth_response."""
        host = "localhost"
        wsgi_app = _RedirectWSGIApp("The authentication flow has completed. You may close this window.")

        # Fail fast if the address is occupied
        simple_server.WSGIServer.allow_reuse_address = False
        with simple_server.make_server(host, 0, wsgi_app) as local_server:
            redirect_uri = f"http://{host}:{local_server.server_port}/"
            updated_url = self.update_url(auth_url, redirect_uri)

            webbrowser.open(url=updated_url, new=1)
            print(f"Please visit this URL to authorize this application: {updated_url}")
            local_server.handle_request()  # serve one request, then exit

        # OAuth 2.0 should only occur over https.
        auth_response = wsgi_app.last_request_uri.replace("http", "https")
        return {"response": auth_response, "redirect_uri": redirect_uri}

    def update_url(self, url, redirect_uri=None):
        if not redirect_uri:
            # nothing to update
            return url

        # add this redirect uri to the url
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params['redirect_uri'] = redirect_uri

        # reconstruct the query string
        query_string = urlencode(query_params, doseq=True)

        # reconstruct the final URL
        return urlunparse(parsed_url._replace(query=query_string))
