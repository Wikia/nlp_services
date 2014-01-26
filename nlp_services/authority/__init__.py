"""
This is an interface for authority data access within this library
"""

from .. import RestfulResource


class PageAuthorityService(RestfulResource):

    def get(self, doc_id):
        raise NotImplementedError("If this isn't cached, you don't get it")


class WikiAuthorityService(RestfulResource):

    def get(self, wiki_id):
        raise NotImplementedError("This needs to be cached, sucka")


class WikiPageRankService(RestfulResource):

    def get(self, wiki_id):
        raise NotImplementedError("Why ain't you cached this awready")


class WikiAuthorCentralityService(RestfulResource):

    def get(self, wiki_id):
        raise NotImplementedError("Gotta cache it first")