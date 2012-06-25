Flask-OAuthProvider
===================

Flask-OAuthProvider is an extension that makes it easy to secure your views 
with OAuth::

    @provider.require_oauth()
    def user_feed(self):
        ...

It gives you fine grained control over access through the use of __realms__::

    @provider.require_oauth(realm="photos")
    def user_photos(self):
        ...

As well as the OAuth parameters such as client key and token::

    @provider.require_oauth()
    def whoami(self):
        return request.oauth.client_key


Usage
-----

Flask-OAuthProvider builds opon OAuthLib and its OAuth 1 RFC 5849 Server class.
You will need to implement a number of abstract methods, required from either
Server (OAuthLib) or OAuthProvider(Flask-OAuthProvider). These methods are 
mainly data storage or retrieval methods since no assumptions are made about
the persistence system you use and as such you are free to use any you see fit.

Take a look at the example application for a fully working, SQLite / SQLAlchemy
backed OAuth provider in the /examples folder.

While implementing your provider class you want to give `OAuthLib Server docs`_
and the `OAuthProvider source`_ a thorough read.

When done, it will be easy to secure your API with OAuth::

    app = Flask(__name__)
    provider = YourProvider(app)

    @app.route("/my_secrets")
    @provider.require(realm="secrets")
    def my_secrets(self):
        ...

Install
-------

Flask-OAuthProvider is easily installed using pip::

    pip install flask-oauthprovider
