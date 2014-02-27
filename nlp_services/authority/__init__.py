"""
This is an interface for authority data access within this library
"""

from .. import RestfulResource
from ..caching import cached_service_request
from ..discourse.entities import WikiPageToEntitiesService
from boto import connect_s3
from multiprocessing import Pool
import json


class PreCachedService(RestfulResource):

    def __init__(self):
        self.bucket = connect_s3().get_bucket('nlp-data')

    def get(self, doc_id):
        key = self.bucket.get_key('service_responses/%s/%s.get' % (doc_id.replace('_', '/'), self.__class__.__name__))
        if key is None or not key.exists():
            return {'status': 500, 'message': 'Not pre-cached'}
        return {'status': 200, doc_id: json.loads(key.get_contents_as_string())}


class PageAuthorityService(PreCachedService):
    pass


class WikiAuthorityService(PreCachedService):
    pass


class WikiPageRankService(PreCachedService):
    pass


class WikiAuthorCentralityService(PreCachedService):
    pass


def watp_mapper(doc_id):
    return doc_id, PageAuthorityService().get_value(doc_id)


class WikiAuthorsToIdsService(RestfulResource):

    @cached_service_request
    def get(self, wiki_id):
        resp = WikiAuthorityService().get(wiki_id)
        if resp.get('status', 500) == 500:
            return resp

        # need to find a way to manage number of processes across library
        p = Pool(processes=32)
        r = p.map_async(watp_mapper, resp[wiki_id].keys())
        r.wait()

        return {'status': 200, wiki_id: dict([(a['user'], a['userid']) for page, authors in r.get() for a in authors])}


class WikiAuthorsToPagesService(RestfulResource):

    @cached_service_request
    def get(self, wiki_id):
        resp = WikiAuthorityService().get(wiki_id)
        if resp.get('status', 500) == 500:
            return resp

        # need to find a way to manage number of processes across library
        p = Pool(processes=32)
        r = p.map_async(watp_mapper, resp[wiki_id].keys())
        r.wait()

        author_to_pages = {}
        for doc_id, authors in r.get():
            for author in authors:
                author_to_pages[author['user']] = (author_to_pages.get(author['user'], [])
                                                   + [(doc_id, author['contribs'])])

        for author in author_to_pages:
            author_to_pages[author] = dict(author_to_pages[author])

        return {'status': 200, wiki_id: author_to_pages}


class WikiTopicAuthorityService(RestfulResource):

    @cached_service_request
    def get(self, wiki_id):
        wpe_resp = WikiPageToEntitiesService().get(wiki_id)
        if wpe_resp.get('status', 500) == 500:
            return wpe_resp
        pages_to_entities = wpe_resp[wiki_id]

        was_resp = WikiAuthorityService().get(wiki_id)
        if was_resp.get('status', 500) == 500:
            return was_resp
        pages_to_authority = was_resp[wiki_id]

        topics_to_authority = dict()
        min_authority = min(pages_to_authority.values())
        for doc_id, entity_data in pages_to_entities.items():
            entity_list = list(set(entity_data.get('redirects', {}).values() + entity_data.get('titles')))
            for entity in entity_list:
                topics_to_authority[entity] = (
                    topics_to_authority.get(entity, 0) + pages_to_authority.get(doc_id, min_authority)
                )

        return {'status': 200, wiki_id: topics_to_authority}


class WikiAuthorTopicAuthorityService(RestfulResource):

    @cached_service_request
    def get(self, wiki_id):
        wpe_resp = WikiPageToEntitiesService().get(wiki_id)
        if wpe_resp.get('status', 500) == 500:
            return wpe_resp
        pages_to_entities = wpe_resp[wiki_id]

        watp_resp = WikiAuthorsToPagesService().get(wiki_id)
        if watp_resp.get('status', 500) == 500:
            return watp_resp
        authors_to_pages = watp_resp[wiki_id]

        was_resp = WikiAuthorityService().get(wiki_id)
        if was_resp.get('status', 500) == 500:
            return was_resp
        pages_to_authority = was_resp[wiki_id]

        authors_to_entities = {}
        authors_to_entities_weighted = {}
        # todo async
        for page, entity_data in pages_to_entities.items():
            entity_list = list(set(entity_data.get('redirects', {}).values() + entity_data.get('titles')))
            for author, author_contribs in filter(lambda x: page in x[1], authors_to_pages.items()):
                if author not in authors_to_entities:
                    authors_to_entities[author] = dict()
                if author not in authors_to_entities_weighted:
                    authors_to_entities_weighted[author] = dict()
                for entity in entity_list:
                    authors_to_entities[author][entity] = (authors_to_entities[author].get(entity, 0)
                                                           + pages_to_authority[page])
                    authors_to_entities_weighted[author][entity] = (authors_to_entities[author].get(entity, 0)
                                                                    + pages_to_authority[page] * author_contribs[page])

        return {'status': 200, wiki_id: {'unweighted': authors_to_entities, 'weighted': authors_to_entities_weighted}}


class WikiTopicsToAuthorityService(RestfulResource):

    @cached_service_request
    def get(self, wiki_id):
        tta_resp = WikiTopicAuthorityService().get(wiki_id)
        if tta_resp.get('status', 500) != 200:
            return tta_resp
        topics_to_authority = tta_resp[wiki_id]
        tta_items = topics_to_authority.items()

        taresp = WikiAuthorTopicAuthorityService().get(wiki_id)
        if taresp.get('status', 500) != 200:
            return taresp
        topic_authority_data = taresp[wiki_id]

        topics_and_authors = []
        for author in topic_authority_data['weighted']:
            for topic in topic_authority_data['weighted'][author]:
                obj = dict(topic=topic,
                           author=author,
                           topic_authority=topic_authority_data['weighted'][author][topic])
                topics_and_authors.append(obj)

        resp = [(topic,
                 dict(authority=authority,
                      authors=sorted(filter(lambda x: x['topic'] == topic, topics_and_authors),
                                     key=lambda y: y['topic_authority'],
                                     reverse=True)[:20])
                 )
                for topic, authority in tta_items]
        return {'status': 200, wiki_id: resp}
