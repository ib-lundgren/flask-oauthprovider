Flask-OAuthProvider
===================

Flask-OAuthProvider is an extension that makes it easy to secure your views 
with OAuth::

    @provider.require_oauth()
    def user_feed(self):
        ...

It gives you fine grained control over access through the use of *realms*::

    @provider.require_oauth(realm="photos")
    def user_photos(self):
        ...

As well as the OAuth parameters such as client key and token::

    @provider.require_oauth()
    def whoami(self):
        return request.oauth.client_key


**Note this extension does NOT give you an OAuth client.** For that simply use
`requests`_ which has OAuthLib backed OAuth support built in. If you want to
know more about OAuth check out the excellent guide at `hueniverse`_ or dig
into the very readable `OAuth 1 RFC 5849 spec`_.

.. _`requests`: https://github.com/kennethreitz/requests
.. _`hueniverse`: http://hueniverse.com/oauth/
.. _`OAuth 1 RFC 5849 spec`: http://tools.ietf.org/html/rfc5849

Usage
-----

Flask-OAuthProvider builds opon `OAuthLib`_ and its `OAuth 1 RFC 5849 Server`_ class.
You will need to implement a number of abstract methods, required from either
Server (`OAuthLib`_) or OAuthProvider(Flask-OAuthProvider). These methods are 
mainly data storage or retrieval methods. No assumptions are made about
the persistence system you use and as such you are free to use any you see fit.

Take a look at the example application for a fully working, SQLite / SQLAlchemy
backed OAuth provider in the `/examples`_ folder.

While implementing your provider class you want to give `OAuthLib Server docs`_
and the `OAuthProvider source`_ a thorough read.

The implementation guide is on its way, feel free to take a look at the overview
pictures of how Flask-OAuthProvider and OAuthLib fit into the OAuth workflow.

* `Client registration`_
* `Request tokens`_
* `Access tokens`_
* `Request verification`_

When you have hacked together a shiny provider class it will be easy to secure your API with OAuth::

    app = Flask(__name__)
    provider = YourProvider(app)

    @app.route("/my_secrets")
    @provider.require(realm="secrets")
    def my_secrets(self):
        ...


.. _`OAuth 1 RFC 5849 Server`: https://github.com/idan/oauthlib/blob/master/oauthlib/oauth1/rfc5849/__init__.py
.. _`OAuthLib`: https://github.com/idan/oauthlib
.. _`/examples`: https://github.com/ib-lundgren/flask-oauthprovider/tree/master/examples
.. _`OAuthLib Server docs`: https://github.com/idan/oauthlib/blob/master/docs/server.rst
.. _`OAuthProvider source`: https://github.com/ib-lundgren/flask-oauthprovider/blob/master/flask_oauthprovider.py
.. _`Client registration`: https://github.com/ib-lundgren/flask-oauthprovider/raw/master/docs/images/client_registration.png
.. _`Request tokens`: https://github.com/ib-lundgren/flask-oauthprovider/raw/master/docs/images/request_token.png
.. _`Access tokens`: https://github.com/ib-lundgren/flask-oauthprovider/raw/master/docs/images/access_token.png 
.. _`Request verification`: https://github.com/ib-lundgren/flask-oauthprovider/raw/master/docs/images/request_verification.png

Install
-------

Flask-OAuthProvider will be easily installed using pip when OAuthLib 0.2.0 is available on pypi  ::

    pip install flask-oauthprovider

