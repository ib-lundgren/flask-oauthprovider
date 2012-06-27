from client import app
app.config["OAUTH_CREDENTIALS"] = {
    u"client_secret": u"WgzyivpCPl7WuaxuSBoCCPv5UP9iBV"
}
app.config["CLIENT_KEY"] = u"06NvHxcvImyIBiXPFsQA6GWJXjC8UU"
app.run(debug=True, port=5001)
