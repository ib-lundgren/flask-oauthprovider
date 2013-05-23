# -*- coding: utf-8 -*-
from oauthlib.oauth1.rfc5849 import Server
from oauthlib.oauth1.rfc5849.signature import collect_parameters
from oauthlib.common import add_params_to_uri, encode_params_utf8
from oauthlib.common import generate_token, urlencode
from flask import Response, request, redirect
from werkzeug.exceptions import Unauthorized, BadRequest
from functools import wraps
from urlparse import urlparse


class OAuthProvider(Server):
    """Provide secure services using OAuth 1 RFC 5849.

    OAuthProvider is based on the secure and highly configurable Server
    base class of oauthlib.oauth.rfc5849 for OAuth 1 providers. This flask
    extension adds a number of convenience methods to act as helpers and a base.

    A number of additional methods that will need to be implemented are added
    and documented as to how they fit into the whole OAuth workflow. Detailed
    descriptions of these methods are provided in respective method __doc__.

    Providers will have to implement the following methods:

    * register(self)
    * save_timestamp_and_nonce(self, client_key, timestamp, nonce,
            request_token=None, access_token=None
    * authorize(self)
    * get_callback(self, request_token)
    * save_request_token(self, client_key, request_token, callback, realm=None,
            secret=None)
    * save_verifier(self, client_key, request_token, verifier)
    * save_access_token(self, client_key, request_token, realm=None,
            secret=None)

    Furthermore 4 default URLs are automatically routed using these properties:

    * request_token_url
    * access_token_url
    * register_url
    * authorize_url

    Request tokens and access tokens will automatically be generated and
    returned to clients. They will be saved using the abstract methods outlined
    earlier.

    A successful provider implementation will enable views to be easily and
    securely protected. Providers will also enjoy fine-grained control over
    which clients can access which resources through the use of realms.

    Follows are two view functions, the first under the default non-specified
    realm and the second under the photos realm.

    @app.route("/status_feed")
    @provider.require_oauth()
    def status_feed(self):
        ...

    @app.route("/photos")
    @provider.require_oauth(realm="photos")
    def photos(self):
        ...

    """

    # Properties used to configure the application, can safely be overloaded

    @property
    def request_token_url(self):
        return u'/request_token'

    @property
    def access_token_url(self):
        return u'/access_token'

    @property
    def register_url(self):
        return u'/register'

    @property
    def authorize_url(self):
        return u'/authorize'

    @property
    def secret_length(self):
        return 30

    # Methods that must be overloaded

    def register(self):
        """Client registration.

        Defaults to /register URL.

        A few common actions during client registration includes:

        * Ask the client for an application name and description
        * Ask the client for one or several callback URIs
        * Allow the client to upload a public RSA key if the RSA signature
          method is supported.

        Upon registration each client must be provided with a client key. If
        the HMAC signature method is used a client secret should also be
        be provided.

        For your convenience the following methods are provided:

        * generate_client_key(self) for the client/consumer key
        * generate_client_secret(self) for the client/consumer secret
        """
        raise NotImplementedError("Must be implemented by inheriting classes")

    def save_timestamp_and_nonce(self, client_key, timestamp, nonce,
            request_token=None, access_token=None):
        """All timestamp and nonces must be stored.

        It is recommended that they are also connected to at least the client
        but preferably also the resource owner/user.
        """
        raise NotImplementedError("Must be implemented by inheriting classes")

    def authorize(self):
        """Ask the user to authorize access to the client.

        Defaults to /authorize URL. Invoked by user (redirected by the client).

        This view should only be accessible by authenticated users, redirect
        unauthenticated users to a login.

        Authorization is commonly done through a form asking the user to
        grant or deny access. This form should also include information that
        help the user identify which client it is authorizing access to.
        Usually by displaying application name and description.

        To the authorization URL the client will append the oauth_token parameter
        which corresponds to the previously obtained request token. This token
        should be validated using self.validate_request_token method.

        The request token should be securely kept, preferably in an encrypted
        HTTPOnly secure cookie during form submission as it will be needed to
        complete the authorization.

        Upon user authorization you should use the authorized method to easily
        generate and return a verifier code to the client.

        def authorize(self):
            ...
            return authorized(request_token)

        If the user denied access or if the request token was invalid it is
        important to not redirect the user back to the client.
        """
        raise NotImplementedError("Must be implemented by inheriting classes")


    def get_callback(self, request_token):
        """Return the callback associated with the request token."""
        raise NotImplementedError("Must be implemented by inheriting classes")

    def save_request_token(self, client_key, request_token, callback, realm=None,
            secret=None):
        """Store request tokens.

        This method is invoked by the request_token view and all you need to do
        is to store the token and its associated realm and token secret.
        """
        raise NotImplementedError("Must be implemented by inheriting classes")

    def save_verifier(self, request_token, verifier):
        """Store verifier and user associated with a specific request token.

        This method is invoked automatically by authorized.

        It is VITAL that you relate the user who authorized access with this
        verifier and request token or else you will be unable to provide
        access to the correct resources later.

        Since invocation of this method originates from the user accessing
        the authorize view you should be able to extract their ID easily from
        the request object.
        """
        raise NotImplementedError("Must be implemented by inheriting classes")

    def save_access_token(self, client_key, access_token, request_token,
            secret=None):
        """Store access tokens.

        This method is invoked by the access_token view and there are two
        tasks you will need to carry out in addition to storing the token:

        1. Retrieve the associated user and realm using request_token
        2. Associate the realm and user with the new access token
        """
        raise NotImplementedError("Must be implemented by inheriting classes")

    # There be dragons beyond this point, tread lightly.

    def __init__(self, app):
        """Setup routes and OAuth token methods."""
        self.request_token = self.require_oauth(require_resource_owner=False)(self.request_token)
        self.access_token = self.require_oauth(require_verifier=True)(self.access_token)
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        """Setup the 4 default routes."""
        app.add_url_rule(self.request_token_url, view_func=self.request_token,
                         methods=[u'POST'])
        app.add_url_rule(self.access_token_url, view_func=self.access_token,
                         methods=[u'POST'])
        app.add_url_rule(self.register_url, view_func=self.register,
                         methods=[u'GET', u'POST'])
        app.add_url_rule(self.authorize_url, view_func=self.authorize,
                         methods=[u'GET', u'POST'])

    def authorized(self, request_token):
        """Create a verifier for an user authorized client"""
        verifier = generate_token(length=self.verifier_length[1])
        self.save_verifier(request_token, verifier)
        response = [
            (u'oauth_token', request_token),
            (u'oauth_verifier', verifier)
        ]
        callback = self.get_callback(request_token)
        return redirect(add_params_to_uri(callback, response))

    def request_token(self):
        """Create an OAuth request token for a valid client request.

        Defaults to /request_token. Invoked by client applications.
        """
        client_key = request.oauth.client_key
        realm = request.oauth.realm
        # TODO: fallback on default realm?
        callback = request.oauth.callback_uri
        request_token = generate_token(length=self.request_token_length[1])
        token_secret = generate_token(length=self.secret_length)
        self.save_request_token(client_key, request_token, callback,
            realm=realm, secret=token_secret)
        return urlencode([(u'oauth_token', request_token),
                          (u'oauth_token_secret', token_secret),
                          (u'oauth_callback_confirmed', u'true')])

    def access_token(self):
        """Create an OAuth access token for an authorized client.

        Defaults to /access_token. Invoked by client applications.
        """
        access_token = generate_token(length=self.access_token_length[1])
        token_secret = generate_token(self.secret_length)
        client_key = request.oauth.client_key
        self.save_access_token(client_key, access_token,
            request.oauth.resource_owner_key, secret=token_secret)
        return urlencode([(u'oauth_token', access_token),
                          (u'oauth_token_secret', token_secret)])

    def generate_client_key(self):
        return generate_token(length=self.client_key_length[1])

    def generate_client_secret(self):
        return generate_token(length=self.secret_length)

    def require_oauth(self, realm=None, require_resource_owner=True,
            require_verifier=False, require_realm=False):
        """Mark the view function f as a protected resource"""

        def decorator(f):
            @wraps(f)
            def verify_request(*args, **kwargs):
                """Verify OAuth params before running view function f"""
                try:
                    if request.form:
                        body = request.form.to_dict()
                    else:
                        body = request.data.decode("utf-8")
                    verify_result = self.verify_request(request.url.decode("utf-8"),
                            http_method=request.method.decode("utf-8"),
                            body=body,
                            headers=request.headers,
                            require_resource_owner=require_resource_owner,
                            require_verifier=require_verifier,
                            require_realm=require_realm or bool(realm),
                            required_realm=realm)
                    valid, oauth_request = verify_result
                    if valid:
                        request.oauth = self.collect_request_parameters(request)

                        # Request tokens are only valid when a verifier is too
                        token = {}
                        if require_verifier:
                            token[u'request_token'] = request.oauth.resource_owner_key
                        else:
                            token[u'access_token'] = request.oauth.resource_owner_key

                        # All nonce/timestamp pairs must be stored to prevent
                        # replay attacks, they may be connected to a specific
                        # client and token to decrease collision probability.
                        self.save_timestamp_and_nonce(request.oauth.client_key,
                                request.oauth.timestamp, request.oauth.nonce,
                                **token)

                        # By this point, the request is fully authorized
                        return f(*args, **kwargs)
                    else:
                        # Unauthorized requests should not diclose their cause
                        raise Unauthorized()

                except ValueError as err:
                    # Caused by missing of or badly formatted parameters
                    raise BadRequest(err.message)

            return verify_request
        return decorator

    def collect_request_parameters(self, request):
        """Collect parameters in an object for convenient access"""

        class OAuthParameters(object):
            """Used as a parameter container since plain object()s can't"""
            pass

        # Collect parameters
        query = urlparse(request.url.decode("utf-8")).query
        content_type = request.headers.get('Content-Type', '')
        if request.form:
            body = request.form.to_dict()
        elif content_type == 'application/x-www-form-urlencoded':
            body = request.data.decode("utf-8")
        else:
            body = ''
        headers = dict(encode_params_utf8(request.headers.items()))
        params = dict(collect_parameters(uri_query=query, body=body, headers=headers))

        # Extract params and store for convenient and predictable access
        oauth_params = OAuthParameters()
        oauth_params.client_key = params.get(u'oauth_consumer_key')
        oauth_params.resource_owner_key = params.get(u'oauth_token', None)
        oauth_params.nonce = params.get(u'oauth_nonce')
        oauth_params.timestamp = params.get(u'oauth_timestamp')
        oauth_params.verifier = params.get(u'oauth_verifier', None)
        oauth_params.callback_uri = params.get(u'oauth_callback', None)
        oauth_params.realm = params.get(u'realm', None)
        return oauth_params
