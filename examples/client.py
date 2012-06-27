"""
A demonstrative OAuth client to use with our provider

This serves as a base, use hmac_client.py, rsa_client.py or
plaintext_client.py depending on which signature type you wish to test.
"""
import requests
from requests.auth import OAuth1
from flask import Flask, redirect, request, session
from urlparse import parse_qsl, urlparse

app = Flask(__name__)
# OBS!: Due to cookie saving issue on localhost client.local is used
# and must be setup in for example /etc/hosts
app.config.update(
    SECRET_KEY="not very secret",
    SERVER_NAME="client.local:5001"
)


@app.route("/start")
def start():
    client = OAuth1(app.config["CLIENT_KEY"],
        callback_uri=u"http://client.local:5001/callback",
        **app.config["OAUTH_CREDENTIALS"])

    r = requests.post(u"http://127.0.0.1:5000/request_token?realm=secret", auth=client)
    data = dict(parse_qsl(r.content))
    resource_owner = data.get(u'oauth_token')
    session["token_secret"] = data.get('oauth_token_secret').decode(u'utf-8')
    url = u"http://127.0.0.1:5000/authorize?oauth_token=" + resource_owner
    return redirect(url)


@app.route("/callback")
def callback():
    # Extract parameters from callback URL
    data = dict(parse_qsl(urlparse(request.url).query))
    resource_owner = data.get(u'oauth_token').decode(u'utf-8')
    verifier = data.get(u'oauth_verifier').decode(u'utf-8')
    token_secret = session["token_secret"]

    # Request the access token
    client = OAuth1(app.config["CLIENT_KEY"],
        resource_owner_key=resource_owner,
        resource_owner_secret=token_secret,
        verifier=verifier,
        **app.config["OAUTH_CREDENTIALS"])
    r = requests.post(u"http://127.0.0.1:5000/access_token", auth=client)

    # Extract the access token from the response
    data = dict(parse_qsl(r.content))
    resource_owner = data.get(u'oauth_token').decode(u'utf-8')
    resource_owner_secret = data.get(u'oauth_token_secret').decode(u'utf-8')
    client = OAuth1(app.config["CLIENT_KEY"],
        resource_owner_key=resource_owner,
        resource_owner_secret=resource_owner_secret,
        **app.config["OAUTH_CREDENTIALS"])
    r = requests.get(u"http://127.0.0.1:5000/protected", auth=client)
    r = requests.get(u"http://127.0.0.1:5000/protected_realm", auth=client)
    return r.content
