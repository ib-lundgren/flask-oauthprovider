from os.path import join, dirname
from client import app


def fread(fn):
    with open(join(dirname(__file__), fn), 'r') as f:
        return f.read().decode("utf-8")

app.config["OAUTH_CREDENTIALS"] = {
    u"rsa_key": fread("mykey.pem"),
    u"signature_method": u"RSA-SHA1",
    "signature_type": "body"
}
app.config["CLIENT_KEY"] = u"5kCCg9t3amq636IsP6PcDGwdJhgdRG"
app.run(debug=True, port=5001)
