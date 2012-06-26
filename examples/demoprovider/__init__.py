from flask import Flask
from provider import ExampleProvider

app = Flask(__name__)
provider = ExampleProvider(app)

import logging
logging.basicConfig(level=logging.DEBUG)


@app.route("/protected")
@provider.require_oauth()
def protected_view():
    #TODO: store something user related
    return "Hej"


@app.route("/protected_realm")
@provider.require_oauth(realm="secret")
def protected_realm_view():
    #TODO: store something user related
    return "Hej secret"



app.run(debug=True)
