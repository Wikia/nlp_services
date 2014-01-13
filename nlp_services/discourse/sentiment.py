"""
Classes for handling sentiment
"""

from multiprocessing import Pool, Manager

import numpy
import string
from nltk.tree import Tree
from ..caching import cached_service_request
from ..title_confirmation import preprocess
from .. import RestfulResource
from .. import document_access
from .entities import CoreferenceCountsService, CombinedEntitiesService, WpEntitiesService


USE_MULTIPROCESSING = False
MP_NUM_CORES = 4


class DocumentSentimentService(RestfulResource):

    """
    Responsible for delivering sentiment information for a given document.
    """

    def __init__(self):
        self.val_to_canonical = dict()
        self.phrases_to_sentiment = dict()


    @cached_service_request
    def get(self, doc_id):
        """
        Provides average sentiment across the document, and sentiment scores for entities within each subject.
        :param doc_id: the id of the document
        :type doc_id: str
        :return: dictionary with response data
        :rtype:dict
        """

        document = document_access.get_document_by_id(doc_id)
        if document is None:
            return {'status': 400, doc_id: {}, 'message': 'Document was empty'}

        response = dict()
        if len(document.sentences) == 0:
            response['status'] = 500
            response['message'] = 'No sentences in this parse.'
            return response

        if document.sentiment is None:
            response['status'] = 500
            response['message'] = 'Sentiment data missing from parse.'
            return response

        response['averageSentiment'] = document.sentiment

        doc_paraphrases = CoreferenceCountsService().get_value(doc_id, {}).get('paraphrases', {})

        self.val_to_canonical = dict(map(lambda x: map(preprocess, x),
                                         [(key, key) for key in doc_paraphrases]
                                         + [(value, key) for key in doc_paraphrases for value in doc_paraphrases[key]]))

        if '' in self.val_to_canonical:
            del self.val_to_canonical['']  # wat

        map(self.traverse_tree_for_sentiment, document.sentences)

        for sentence in document.sentences:
            self.traverse_tree_for_sentiment(sentence)

        response['averagePhraseSentiment'] = dict([(x[0], numpy.mean(filter(lambda y: y is not None, x[1]))) for x in self.phrases_to_sentiment.items()])

        return {'status': 200, doc_id: response}

    def traverse_tree_for_sentiment(self, sentence, subtree=None):
        """
        Cross-references sentiment for a sentence with the mentions therein
        :param sentence: a sentence instance
        :type sentence:class:`corenlp_xml.document.Sentence`
        :param subtree: an instance of an NLTK tree, unde whose scope we operate
        :type subtree:class:`nltk.tree.Tree`
        :return: None, stores values in class as side effect
        :rtype: None
        """
        exclude = set(string.punctuation)
        try:
            if subtree is None:
                subtree = sentence.parse
            if not isinstance(subtree, Tree):
                return None
            flattened = preprocess(' '.join(subtree.leaves()))
            if flattened in self.val_to_canonical:
                self.phrases_to_sentiment[flattened] = self.phrases_to_sentiment.get(self.val_to_canonical[flattened], []) \
                                                       + [sentence.sentiment]
                return None  # no need to keep going
            elif subtree.node in ['NP', 'NNS', 'NN', 'NNP', 'NNPS', 'VBG'] and flattened.strip() != '':
                self.phrases_to_sentiment[flattened] = self.phrases_to_sentiment.get(flattened, []) + [sentence.sentiment]

            map(lambda x: self.traverse_tree_for_sentiment(sentence, x), filter(lambda x: isinstance(x, Tree), subtree))
        except UnicodeEncodeError:
            pass
        return None


class BaseDocumentEntitySentimentService(RestfulResource):
    _entities_service = None

    ''' Filters out sentiment in a document to only care about entities '''
    @cached_service_request
    def get(self, doc_id):
        """
        Applies sentiment to a set of entities
        """
        sentiment_response = DocumentSentimentService().get(doc_id)

        if sentiment_response['status'] is not 200:
            return sentiment_response

        entities = self._entities_service().get_value(doc_id, [])

        return {'status': 200,
                doc_id: dict(filter(lambda x: x[0] in entities,
                                    sentiment_response[doc_id]['averagePhraseSentiment'].items()))
                }


class DocumentEntitySentimentService(BaseDocumentEntitySentimentService):
    _entities_service = CombinedEntitiesService


class WpDocumentEntitySentimentService(BaseDocumentEntitySentimentService):
    _entities_service = WpEntitiesService


class BaseWikiEntitySentimentService(RestfulResource):
    """ Does document entity sentiment service across all documents """
    _document_entity_sentiment_service = None

    @classmethod
    def update_dict_with_document_entity_sentiment(cls, tup):
        """
        Updates a managed dict with entity sentiment values in multiprocessing paradigm
        :param tup: a tuple containing the managed dict, the doc id, and the class to use
        :type tup: tuple
        """
        managed, doc_id = tup
        service_response = cls._document_entity_sentiment_service().get_value(doc_id, {})
        for key in service_response:
            managed[key] = managed.get(key, []) + [service_response[key]]


    @cached_service_request
    def get(self, wiki_id):
        """
        Averages sentiment for entities across all documents
        :param wiki_id: the id of the wiki
        :type wiki_id: str|int
        :return: response
        :rtype: dict
        """
        global USE_MULTIPROCESSING, MP_NUM_CORES

        page_doc_response = document_access.ListDocIdsService().get(wiki_id)
        if page_doc_response['status'] != 200:
            return page_doc_response

        if USE_MULTIPROCESSING:
            d = Manager().dict()

            Pool(processes=MP_NUM_CORES).map(self.__class__.update_dict_with_document_entity_sentiment(),
                                             [(d, doc_id) for doc_id in page_doc_response[wiki_id]])
            entity_sentiment = dict(d.items())
        else:
            entity_sentiment = {}
            dss = self._document_entity_sentiment_service()
            counter = 0
            total = len(page_doc_response[wiki_id])
            for doc_id in page_doc_response[wiki_id]:
                sent_response = dss.get_value(doc_id, {})
                avg_phrase_sentiment = sent_response.get('averagePhraseSentiment', {})
                print "%d / %d (%d keys)" % (counter, total, len(avg_phrase_sentiment.keys()))
                counter += 1
                for key in avg_phrase_sentiment:
                    entity_sentiment[key] = entity_sentiment.get(key, []) + [avg_phrase_sentiment[key]]

        return {'status': 200,
                wiki_id: dict([(key, numpy.mean([i+1 for i in entity_sentiment[key]])+1) for key in entity_sentiment])}


class WikiEntitySentimentService(BaseWikiEntitySentimentService):
    _document_entity_sentiment_service = DocumentEntitySentimentService


class WpWikiEntitySentimentService(BaseWikiEntitySentimentService):
    _document_entity_sentiment_service = WpDocumentEntitySentimentService
