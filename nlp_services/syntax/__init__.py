"""
Services focused on accessing and traversing syntactic data
"""

from mrg_utils.sentence import Sentence as MrgSentence

from .. import RestfulResource
from .. import document_access
from ..title_confirmation import preprocess
from ..caching import cached_service_request

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

def get_pos_phrases(doc_id, phrases):
    """
    Given a doc ID, return a list of
    :param doc_id: The ID of the document
    :type doc_id: str
    :param phrases: a list of POS tags desired
    :type phrases: list
    :return: a list of strings corresponding with the spans matching the desired phrases or words
    """
    leaves = []
    document = document_access.get_document_by_id(doc_id)
    if document is not None:
        leaves = [u" ".join(subtree.leaves())
                  for s in document.sentences
                  for subtree in s.parse.subtrees()
                  if subtree.node in phrases]

    return leaves


class AllNounPhrasesService(RestfulResource):

    """ Read-only service that gives all noun phrases for a document """

    @cached_service_request
    def get(self, doc_id):
        """ Get noun phrases for a document
        :param doc_id: the id of the document in Solr
        :type doc_id: str
        :return: a response in the proper format
        :rtype: dict
        """
        return {doc_id: get_pos_phrases(doc_id, [u'NP']), 'status': 200}


class AllVerbPhrasesService(RestfulResource):

    """ Read-only service that gives all verb phrases for a document """

    @cached_service_request
    def get(self, doc_id):
        """
        Get verb phrases for a document
        :param doc_id: the id of the document in Solr
        :type doc_id: str
        :return: a response in the proper format
        :rtype: dict
        """
        return {doc_id: get_pos_phrases.get(doc_id, [u'VP']), 'status': 200}


class HeadsService(RestfulResource):

    """ Provides syntactic heads for a given document """

    @cached_service_request
    def get(self, doc_id):
        """
        Get the string values of the syntactic heads of each sentence
        :param doc_id: the id of the document
        :type doc_id: str
        :return: a response in the proper format
        :rtype: dict
        """
        document = document_access.get_document_by_id(doc_id)
        if document is None:
            return {'status': 404, 'message': 'Document for %s not found' % doc_id}

        retval = []
        counter = 0
        for sentence in document.sentences:
            counter += 1
            retval += [preprocess(MrgSentence(sentence.parse_string, counter).nodes.getTermHead().getString())]

        if len(retval) == 0:
            return {'status': 400, 'message': 'No sentences'}

        return {'status': 200, doc_id: retval}


class WikiToPageHeadsService(RestfulResource):
    """
    Provides heads for each page, as a caching hack
    """
    @cached_service_request
    def get(self, wiki_id):
        """
        Gets all syntactic heads, by page ID, for every sentence in this wiki
        ;param wiki_id: the id of the wiki
        :return: response
        :rtype: dict
        """
        page_doc_response = document_access.ListDocIdsService().get(wiki_id)
        if page_doc_response['status'] != 200:
            return page_doc_response

        page_doc_ids = page_doc_response.get(wiki_id, [])
        total = len(page_doc_ids)
        response = {'status': 200, wiki_id: {}}
        counter = 0
        hs = HeadsService()
        for page_doc_id in page_doc_ids:
            response[wiki_id][page_doc_id] = hs.get_value(page_doc_id, [])
            counter += 1
            print "%d / %d" % (counter, total)
        return response
        #return {'status': 200, wiki_id: dict([(doc_id, hs.get_value(doc_id, [])) for doc_id in page_doc_ids])}


class HeadsCountService(RestfulResource):

    """ Provides a count for all heads in a wiki """

    @cached_service_request
    def get(self, wiki_id):
        """
        Gets all syntactic heads, grouped into counts, for every sentence in this wiki
        ;param wiki_id: the id of the wiki
        :return: response
        :rtype: dict
        """
        page_doc_response = document_access.ListDocIdsService().get(wiki_id)
        if page_doc_response['status'] != 200:
            return page_doc_response

        page_doc_ids = page_doc_response.get(wiki_id, [])
        hs = HeadsService()
        all_heads = [head
                    for heads in filter(lambda x: x is not None, map(hs.get_value, page_doc_ids))
                    for head in heads]
        single_heads = set(all_heads)
        return {'status': 200, wiki_id: dict(zip(single_heads, map(all_heads.count, single_heads)))}


class TopHeadsService(RestfulResource):

    """ Gets the most frequent syntactic in a wiki """
    @cached_service_request
    def get(self, wiki_id):
        """
        Gets the count of heads in a wiki ordered by frequency descending
        :param wiki_id: the id of the wiki
        :return: response
        :rtype: dict
        """
        heads_to_counts = HeadsCountService().get_value(wiki_id, {})
        items = sorted(heads_to_counts.items(),
                       key=lambda item: int(item[1]),
                       reverse=True)

        return {'status': 200, wiki_id: items}
