from flask import request, render_template, g
from flask.ext.oauthprovider import OAuthProvider
from sqlalchemy.orm.exc import NoResultFound
from models import ResourceOwner, Client, Nonce, Callback
from models import RequestToken, AccessToken, db_session
from utils import require_openid


class ExampleProvider(OAuthProvider):

    @property
    def enforce_ssl(self):
        return False

    @property
    def realms(self):
        return [u"secret", u"trolling"]

    @require_openid
    def authorize(self):
        if request.method == u"POST":
            token = request.form.get("oauth_token")
            return self.authorized(token)
        else:
            # TODO: Authenticate client
            token = request.args.get(u"oauth_token")
            return render_template(u"authorize.html", token=token)

    @require_openid
    def register(self):
        if request.method == u'POST':
            client_key = self.generate_client_key()
            secret = self.generate_client_secret()
            # TODO: input sanitisation?
            name = request.form.get(u"name")
            description = request.form.get(u"description")
            callback = request.form.get(u"callback")
            pubkey = request.form.get(u"pubkey")
            # TODO: redirect?
            # TODO: pubkey upload
            # TODO: csrf
            info = {
                u"client_key": client_key,
                u"name": name,
                u"description": description,
                u"secret": secret,
                u"pubkey": pubkey
            }
            client = Client(**info)
            client.callbacks.append(Callback(callback))
            client.resource_owner = g.user
            db_session.add(client)
            db_session.commit()
            return render_template(u"client.html", **info)
        else:
            return render_template(u"register.html")

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce,
            request_token=None, access_token=None):
        filters = [
            Nonce.nonce == nonce,
            Nonce.timestamp == timestamp,
            Client.id == Nonce.client_id,
            Client.client_key == client_key
        ]
        if request_token:
            filters.extend([
                RequestToken.id == Nonce.request_token_id,
                RequestToken.token == request_token
            ])
        if access_token:
            filters.extend([
                AccessToken.id == Nonce.access_token_id,
                AccessToken.token == access_token
            ])
        try:
            db_session.query(Nonce, Client, ResourceOwner).filter(*filters).one()
            return False
        except NoResultFound:
            return True

    def validate_redirect_uri(self, client_key, redirect_uri=None):
        try:
            client = Client.query.filter_by(client_key=client_key).one()
            if redirect_uri in (x.callback for x in client.callbacks):
                return True

            elif len(client.callbacks) == 1 and redirect_uri is None:
                return True

            else:
                return False

        except NoResultFound:
            return False

    def validate_client_key(self, client_key):
        try:
            Client.query.filter_by(client_key=client_key).one()
            return True

        except NoResultFound:
            return False

    def validate_requested_realm(self, client_key, realm):
        return True

    def validate_realm(self, client_key, access_token, uri=None, required_realm=None):

        if not required_realm:
            return True

        # insert other check, ie on uri here

        try:
            token = db_session.query(AccessToken, Client).filter(
                    Client.client_key == client_key,
                    AccessToken.token == access_token).one().AccessToken
            return token.realm in required_realm

        except NoResultFound:
            return False

    @property
    def dummy_client(self):
        return u'dummy_client'

    @property
    def dummy_resource_owner(self):
        return u'dummy_resource_owner'

    def validate_request_token(self, client_key, resource_owner_key):
        # TODO: make client_key optional
        if client_key:
            db_session.query(RequestToken, Client).filter(
                RequestToken.token == resource_owner_key,
                Client.client_key == client_key).one()
        else:
            RequestToken.query.filter_by(token=resource_owner_key).one()
        try:
            return True

        except NoResultFound:
            return False

    def validate_access_token(self, client_key, resource_owner_key):
        try:
            db_session.query(AccessToken, Client).filter(
                Client.client_key == client_key,
                Client.id == AccessToken.client_id,
                AccessToken.token == resource_owner_key
            ).one()
            return True

        except NoResultFound:
            return False

    def validate_verifier(self, client_key, resource_owner_key, verifier):
        try:
            db_session.query(RequestToken, Client).filter(
                Client.client_key == client_key,
                RequestToken.token == resource_owner_key,
                RequestToken.verifier == verifier
            ).one()
            return True
        except NoResultFound:
            return False

    def get_callback(self, request_token):
        return RequestToken.query.filter_by(token=request_token).one().callback

    def get_realm(self, client_key, request_token):
        return db_session.query(RequestToken, Client).filter(
                    Client.client_key == client_key,
                    RequestToken.token == request_token
        ).one().RequestToken.realm

    def get_client_secret(self, client_key):
        try:
            return Client.query.filter_by(client_key=client_key).one().secret

        except NoResultFound:
            return None

    def get_request_token_secret(self, client_key, resource_owner_key):
        try:
            query = db_session.query(RequestToken, Client).filter(
                RequestToken.token == resource_owner_key,
                Client.client_key == client_key
            ).one()
            return query.RequestToken.secret

        except NoResultFound:
            return None

    def get_access_token_secret(self, client_key, resource_owner_key):
        try:
            query = db_session.query(AccessToken, Client).filter(
                AccessToken.token == resource_owner_key,
                Client.client_key == client_key
            ).one()
            return query.AccessToken.secret

        except NoResultFound:
            return None

    def save_request_token(self, client_key, request_token, callback,
            realm=None, secret=None):
        token = RequestToken(request_token, callback, secret=secret, realm=realm)
        token.client = Client.query.filter_by(client_key=client_key).one()
        db_session.add(token)
        db_session.commit()

    def save_access_token(self, client_key, access_token, request_token,
            realm=None, secret=None):
        token = AccessToken(access_token, secret=secret, realm=realm)
        token.client = Client.query.filter_by(client_key=client_key).one()
        req_token = RequestToken.query.filter_by(token=request_token).one()
        token.resource_owner = req_token.resource_owner
        token.realm = req_token.realm
        db_session.add(token)
        db_session.commit()

    def save_timestamp_and_nonce(self, client_key, timestamp, nonce,
            request_token=None, access_token=None):
        nonce = Nonce(nonce, timestamp)
        nonce.client = Client.query.filter_by(client_key=client_key).one()

        if request_token:
            nonce.token = RequestToken.query.filter_by(token=request_token).one()

        if access_token:
            nonce.token = AccessToken.query.filter_by(token=access_token).one()

        db_session.add(nonce)
        db_session.commit()

    def save_verifier(self, request_token, verifier):
        token = RequestToken.query.filter_by(token=request_token).one()
        token.verifier = verifier
        token.resource_owner = g.user
        db_session.add(token)
        db_session.commit()
