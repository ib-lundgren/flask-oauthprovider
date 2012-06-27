from flask import Flask, request
from provider import ExampleProvider
from models import AccessToken

app = Flask(__name__)
app.config.update(
    DATABASE_URI="",
    SECRET_KEY="debugging key"
)

provider = ExampleProvider(app)

# Imported to setup views
import login


@app.route("/protected")
@provider.require_oauth()
def protected_view():
    token = request.oauth.resource_owner_key
    user = AccessToken.query.filter_by(token=token).one().resource_owner
    return user.name


@app.route("/protected_realm")
@provider.require_oauth(realm="secret")
def protected_realm_view():
    token = request.oauth.resource_owner_key
    user = AccessToken.query.filter_by(token=token).one().resource_owner
    return user.email
