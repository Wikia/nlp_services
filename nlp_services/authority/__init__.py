"""
This is an interface for authority data access within this library
"""

from .. import RestfulResource
from boto import connect_s3
import json


class PreCachedService(RestfulResource):

    def __init__(self):
        self.bucket = connect_s3().get_bucket('nlp-data')

    def get(self, doc_id):
        key = self.bucket.get_key('service_responses/%s/%s.get' % (doc_id.replace('_', '/'), self.__class__.__name__))
        if key is None or not key.exists():
            return {'status': 500, 'message': 'Not pre-cached'}
        return {doc_id: json.loads(key.get_contents_as_string())}


class PageAuthorityService(PreCachedService):
    pass


class WikiAuthorityService(PreCachedService):
    pass


class WikiPageRankService(PreCachedService):
    pass


class WikiAuthorCentralityService(PreCachedService):
    pass