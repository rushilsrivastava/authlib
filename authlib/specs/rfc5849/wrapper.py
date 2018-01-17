from authlib.common.urls import urlparse, extract_params, url_decode
from .util import parse_authorization_header
from .signature import (
    SIGNATURE_TYPE_QUERY,
    SIGNATURE_TYPE_BODY,
    SIGNATURE_TYPE_HEADER
)


class OAuth1Request(object):
    def __init__(self, method, uri, body=None, headers=None):
        self.method = method
        self.uri = uri
        self.body = body
        self.headers = headers or {}

        # states namespaces
        self.client = None
        self.token = None
        self.grant_user = None

        self.query = urlparse.urlparse(uri).query
        self.query_params = url_decode(self.query)
        self.body_params = extract_params(body)

        auth = headers.get('Authorization')
        self.realm = None
        if auth:
            self.auth_params = parse_authorization_header(auth, True)
            self.realm = dict(self.auth_params).get('realm')
        else:
            self.auth_params = []

        oauth_params_set = [
            (SIGNATURE_TYPE_QUERY, list(_filter_oauth(self.query_params))),
            (SIGNATURE_TYPE_BODY, list(_filter_oauth(self.body_params))),
            (SIGNATURE_TYPE_HEADER, list(_filter_oauth(self.auth_params)))
        ]
        oauth_params_set = [params for params in oauth_params_set if params[1]]
        if len(oauth_params_set) > 1:
            # TODO
            raise ValueError()

        self.oauth_signature_type = oauth_params_set[0][0]
        self.oauth_params = dict(oauth_params_set[0][1])

        params = {}
        params.update(self.query_params)
        params.update(self.body_params)
        params.update(self.auth_params)
        self.params = params

    @property
    def client_id(self):
        return self.oauth_params.get('oauth_consumer_key')

    @property
    def client_secret(self):
        if self.client:
            return self.client.client_secret

    @property
    def signature(self):
        return self.oauth_params.get('oauth_signature')

    @property
    def signature_method(self):
        return self.oauth_params.get('oauth_signature_method')

    @property
    def resource_owner_key(self):
        return self.oauth_params.get('oauth_token')

    @property
    def resource_owner_secret(self):
        if self.token:
            return self.token.oauth_token_secret


def _filter_oauth(params):
    for k, v in params:
        if k.startswith('oauth_'):
            yield (k, v)
