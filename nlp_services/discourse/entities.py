"""
Handles entity identification

You'll notice that there are base classes and then implementing child classes.
This doesn't scale, but in order to fix this, we'd need to entirely rewrite our caching component.
It costs money to re-cache this shit, so we're not doing that right now.
"""

from .. import document_access
from .. import RestfulResource
from ..pooling import pool
from ..caching import cached_service_request
from ..syntax import AllNounPhrasesService
from ..title_confirmation import confirm, canonical, preprocess


class CoreferenceCountsService(RestfulResource):

    """
    Gets coreference groupings and their counts for a given doc id
    """
    @cached_service_request
    def get(self, doc_id):
        """ Returns coreference and mentions for a document
        :param doc_id: the id of the document in Solr
        """

        document = document_access.get_document_by_id(doc_id)
        if document is None:
            return {'status': 400, doc_id: {}, 'message': 'Document was empty'}

        mention_counts = dict()
        representative_to_mentions = dict()
        if document.coreferences is not None:
            for coreference in document.coreferences:
                representative = coreference.representative
                rep_string = unicode(representative.tokens)
                sibling_strings = [unicode(mention.tokens) for mention in representative.siblings]
                representative_to_mentions[rep_string] = representative_to_mentions.get(rep_string, []) + sibling_strings
                mention_counts[rep_string] = mention_counts.get(rep_string, 0) + 1
                for sib_string in sibling_strings:
                    mention_counts[sib_string] = mention_counts.get(sib_string, 0) + 1

        return {doc_id: {'mentionCounts': mention_counts, 'paraphrases': representative_to_mentions}, 'status': 200}


class BaseEntitiesService(RestfulResource):

    """
    Reusable logic for entity extracting entities from multiple sources
    Identifies, confirms, and counts entities over a given page
    """

    _use_wikia = False
    _use_wikipedia = False

    @cached_service_request
    def get(self, doc_id):
        """
        Use title_confirmation module to make this fast on a per-wiki basis
        :param doc_id: the id of the document
        :type doc_id: str
        :return: a response keying doc id to redirects and titles
        :rtype: dict
        """

        print doc_id
        if not self._use_wikia and not self._use_wikipedia:
            raise Exception("Entity sources aren't configured")

        resp = {'status': 200}

        nps = AllNounPhrasesService().get_value(doc_id)
        if nps is None:
            return {'status': 200, doc_id: {'titles': [], 'redirects': {}}}

        sources = dict()
        if self._use_wikia:
            wiki_id = doc_id.split('_')[0]
            sources['wiki_id'] = wiki_id

        sources['use_wikipedia'] = self._use_wikipedia

        confirmed = list(set(filter(lambda np: confirm(np, **sources), nps)))

        resp['titles'] = confirmed

        if self._use_wikia:
            # todo it would be tight to have wikipedia redirects all figured out at some point
            resp['redirects'] = dict(filter(lambda x: x[0] != x[1],
                                            [(title, canonical(title, wiki_id)) for title in confirmed]))

        print doc_id, "done"
        return {'status': 200, doc_id: resp}


class EntitiesService(BaseEntitiesService):
    _use_wikia = True
    _use_wikipedia = False


class WpEntitiesService(BaseEntitiesService):
    _use_wikia = False
    _use_wikipedia = True


class CombinedEntitiesService(BaseEntitiesService):
    _use_wikia = True
    _use_wikipedia = True


class BaseEntityCountsService(RestfulResource):
    """
    Count entities for a doc ID given different kinds of entity sources and coreference links
    """

    _entity_class = None

    @cached_service_request
    def get(self, doc_id):
        """
        Given a doc id, accesses entities and then cross-references entity parses
        :param doc_id: the id of the article
        :type doc_id: str
        :return: respones
        :rtype: dict
        """
        entitiesresponse = self._entity_class().get_value(doc_id, {})
        coreferences = CoreferenceCountsService().get_value(doc_id, {})

        doc_paraphrases = coreferences.get('paraphrases', {})
        coref_mention_keys = map(preprocess, doc_paraphrases.keys())
        coref_mention_values = map(preprocess, [item for sublist in doc_paraphrases.values() for item in sublist])
        paraphrases = dict([(preprocess(item[0]), map(preprocess, item[1]))
                            for item in doc_paraphrases.items()])

        counts = {}

        for val in entitiesresponse['titles']:
            try:
                val = preprocess(val)
                canonical_value = entitiesresponse['redirects'].get(val, val)
                if canonical_value in coref_mention_keys:
                    counts[canonical_value] = len(paraphrases[canonical_value])
                elif canonical_value != val and val in coref_mention_keys:
                    counts[canonical_value] = len(paraphrases[val])
                elif canonical_value in coref_mention_values:
                    counts[canonical_value] = len(filter(lambda x: canonical_value in x[1], paraphrases.items())[0][1])
                elif canonical_value != val and val in coref_mention_values:
                    counts[canonical_value] = len(filter(lambda x: val in x[1], paraphrases.items())[0][1])
            except Exception as e:
                print e.message

        return {doc_id: counts, 'status': 200}


class EntityCountsService(BaseEntityCountsService):
    _entity_class = EntitiesService


class WpEntityCountsService(BaseEntityCountsService):
    _entity_class = WpEntitiesService


class CombinedEntityCountsService(BaseEntityCountsService):
    _entity_class = CombinedEntitiesService


class BaseWikiEntitiesService(RestfulResource):
    """
    Aggregates entities over a wiki
    """
    _entity_count_service = None

    @cached_service_request
    def get(self, wiki_id):

        """
        Given a wiki doc id, iterates over all documents available.
        For each noun phrase, we confirm whether there is a matching title.
        We then cross-reference that noun phrase by mention count.
        :param wiki_id: the id of the wiki
        :type wiki_id: int|str
        :return: response
        :rtype: dict
        """

        page_doc_response = document_access.ListDocIdsService().get(wiki_id)
        if page_doc_response['status'] != 200:
            return page_doc_response

        entities_to_count = {}
        entity_service = self._entity_count_service()

        counter = 1
        page_doc_ids = page_doc_response.get(wiki_id, [])
        total = len(page_doc_ids)
        for page_doc_id in page_doc_ids:
            entities_with_count = entity_service.get(page_doc_id).get(page_doc_id, {}).items()
            map(lambda x: entities_to_count.__setitem__(x[0], entities_to_count.get(x[0], 0) + x[1]),
                entities_with_count)
            print '(%s/%s)' % (counter, total)
            counter += 1

        counts_to_entities = {}
        for entity in entities_to_count.keys():
            cnt = entities_to_count[entity]
            counts_to_entities[cnt] = counts_to_entities.get(cnt, []) + [entity]

        return {wiki_id: counts_to_entities, 'status': 200}


class WikiEntitiesService(BaseWikiEntitiesService):
    _entity_count_service = EntityCountsService


class WpWikiEntitiesService(BaseWikiEntitiesService):
    _entity_count_service = WpEntityCountsService


class CombinedWikiEntitiesService(BaseWikiEntitiesService):
    _entity_count_service = CombinedEntityCountsService


class BaseTopEntitiesService(RestfulResource):
    _entities_service = None
    """
    Gets top 50 entities for a given wiki
    """
    @cached_service_request
    def get(self, wiki_id):
        counts_to_entities = self._entities_service().get_value(wiki_id, {})
        items = sorted([(val, key) for key in counts_to_entities.keys() for val
                        in counts_to_entities[key]],
                       key=lambda item: int(item[1]),
                       reverse=True)
        return {'status': 200, wiki_id: items[:50]}


class TopEntitiesService(BaseTopEntitiesService):
    _entities_service = WikiEntitiesService


class WpTopEntitiesService(BaseTopEntitiesService):
    _entities_service = WpWikiEntitiesService


class CombinedTopEntitiesService(BaseTopEntitiesService):
    _entities_service = CombinedWikiEntitiesService


class BaseWikiPageEntitiesService(RestfulResource):
    """ Aggregates entities over a wiki by page """
    _entity_count_service = None
    @cached_service_request
    def get(self, wiki_id):
        """
        Given a wiki doc id, iterates over all documents available.
        For each noun phrase, we confirm whether there is a matching title.
        We then cross-reference that noun phrase by mention count.
        :param wiki_id: the id of the wiki
        :type wiki_id: str|int
        :rtype: dict
        :return: response
        """

        page_doc_response = document_access.ListDocIdsService().get(wiki_id)
        if page_doc_response['status'] != 200:
            return page_doc_response

        entity_service = self._entity_count_service()

        return {'status': 200, wiki_id: dict([(page_doc_id, entity_service.get_value(page_doc_id))
                                              for page_doc_id in page_doc_response.get(wiki_id, [])])}


class WikiPageEntitiesService(BaseWikiPageEntitiesService):
    _entity_count_service = EntityCountsService


class WpWikiPageEntitiesService(BaseWikiPageEntitiesService):
    _entity_count_service = WpEntityCountsService


class CombinedWikiPageEntitiesService(BaseWikiPageEntitiesService):
    _entity_count_service = CombinedEntityCountsService


class BaseDocumentCountsService(RestfulResource):
    """ Counts the number of documents each entity appears in """
    _entity_count_service = None

    @cached_service_request
    def get(self, wiki_id):
        """ Given a wiki doc id, iterates over all documents available.
        For each noun phrase, we confirm whether there is a matching title.
        We then cross-reference that noun phrase by document count, not mention count
        :param wiki_id: the id of the wiki
        :type wiki_id: int|str
        :rtype: dict
        :return: response
        """

        page_doc_response = document_access.ListDocIdsService().get(wiki_id)
        if page_doc_response['status'] != 200:
            return page_doc_response

        entities_to_count = {}
        entity_service = self._entity_count_service()

        counter = 1
        page_doc_ids = page_doc_response.get(wiki_id, [])
        total = len(page_doc_ids)
        for page_doc_id in page_doc_ids:
            entities_with_count = entity_service.get(page_doc_id).get(page_doc_id, {}).items()
            map(lambda x: entities_to_count.__setitem__(x[0], entities_to_count.get(x[0], 0) + 1), entities_with_count)
            counter += 1
            print "%d / %d" % (counter, total)

        counts_to_entities = {}
        for entity in entities_to_count.keys():
            cnt = entities_to_count[entity]
            counts_to_entities[cnt] = counts_to_entities.get(cnt, []) + [entity]

        return {wiki_id: counts_to_entities, 'status': 200}


class EntityDocumentCountsService(BaseDocumentCountsService):
    _entity_count_service = EntityCountsService


class WpEntityDocumentCountsService(BaseDocumentCountsService):
    _entity_count_service = WpEntityCountsService


class CombinedDocumentEntityCountsService(BaseDocumentCountsService):
    _entity_count_service = CombinedEntityCountsService


class BaseWikiPageToEntitiesService(RestfulResource):

    def map_pageids(self, pageids):
        return None

    @cached_service_request
    def get(self, wiki_id):
        """ Given a wiki doc id, iterates over all documents available.
        The response is a dictionary that keys documents to entities.
        This is mostly for caching!
        :param wiki_id: the id of the wiki
        :type wiki_id: int|str
        :rtype: dict
        :return: response
        """

        page_doc_response = document_access.ListDocIdsService().get(wiki_id)
        if page_doc_response['status'] != 200:
            return page_doc_response

        page_doc_ids = page_doc_response.get(wiki_id, [])

        print "Getting entities for docs"
        return {wiki_id: dict(zip(page_doc_ids, self.map_pageids(page_doc_ids))), 'status': 200}


def es_get(pageid):
    return EntitiesService().get_value(pageid)


class WikiPageToEntitiesService(BaseWikiPageToEntitiesService):
    def map_pageids(self, pageids):
        return pool(num_processes=32).map_async(es_get, pageids).get()


def wpes_get(pageid):
    return WpEntitiesService().get_value(pageid)


class WpPageToEntitiesService(BaseWikiPageToEntitiesService):
    def map_pageids(self, pageids):
        print pool(with_max=True).map_async(wpes_get, pageids).get()


def ces_get(pageid):
    return CombinedEntitiesService.get_value(pageid)


class CombinedPageToEntitiesService(BaseWikiPageToEntitiesService):
    def map_pageids(self, pageids):
        print pool(with_max=True).map_async(ces_get, pageids).get()
