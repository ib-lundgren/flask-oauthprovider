import pymongo


def get_connection():
    return pymongo.MongoClient().demo_oauth_provider


class Model(dict):
    @classmethod
    def get_collection(cls):
        conn = get_connection()
        return conn[cls.table]
        
    @classmethod
    def find_one(cls, attrs):
        return cls.get_collection().find_one(attrs)
    
    @classmethod
    def insert(cls, obj):
        return cls.get_collection().insert(obj)
        
    @classmethod
    def save(cls, obj):
        return cls.get_collection().save(obj)

    def __getattr__(self, attr):
        return self[attr]
        
    def __setattr__(self, attr, value):
        self[attr] = value
    
    

class ResourceOwner(Model):
    table = "users"

    def __init__(self, name="", email="", openid=""):
        self.name = name
        self.email = email
        self.openid = openid
        self.request_tokens = []
        self.access_tokens = []
        self.client_ids = []

    def __repr__(self):
        return "<ResourceOwner (%s, %s)>" % (self.name, self.email)


class Client(Model):
    table = "clients"

    def __init__(self, client_key, name, description, secret=None, pubkey=None):
        self.client_key = client_key
        self.name = name
        self.description = description
        self.secret = secret
        self.pubkey = pubkey
        self.request_tokens = []
        self.access_tokens = []
        self.callbacks = []
        self.resource_owner_id = ""

    def __repr__(self):
        return "<Client (%s, %s)>" % (self.name, self.id)


class Nonce(Model):
    table = "nonces"

    def __init__(self, nonce, timestamp):
        self.nonce = nonce
        self.timestamp = timestamp
        self.client_id = ""
        self.request_token_id = ""
        self.access_token_id = ""

    def __repr__(self):
        return "<Nonce (%s, %s, %s, %s)>" % (self.nonce, self.timestamp, self.client, self.resource_owner)


class RequestToken(Model):
    table = "requestTokens"

    def __init__(self, token, callback, secret=None, verifier=None, realm=None):
        self.token = token
        self.secret = secret
        self.verifier = verifier
        self.realm = realm
        self.callback = callback
        self.client_id = ""
        self.resource_owner_id = ""
        

    def __repr__(self):
        return "<RequestToken (%s, %s, %s)>" % (self.token, self.client, self.resource_owner)


class AccessToken(Model):
    table = "accessTokens"

    def __init__(self, token, secret=None, verifier=None, realm=None):
        self.token = token
        self.secret = secret
        self.verifier = verifier
        self.realm = realm
        self.client_id = ""
        self.resource_owner_id = ""

    def __repr__(self):
        return "<AccessToken (%s, %s, %s)>" % (self.token, self.client, self.resource_owner)
