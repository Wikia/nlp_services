__author__ = 'relwell'









def update_dict_wpdess(tup):
    managed, doc_id, ids = tup
    ids += [doc_id]
    print len(ids)
    service_response = WpDocumentEntitySentimentService().get_value(doc_id, {})
    for key in service_response:
        managed[key] = managed.get(key, []) + [service_response[key]]


class WpWikiEntitySentimentService(RestfulResource):

    """ Does document entity sentiment service across all documents """
    @cached_service_request
    def get(self, wiki_id):

        global USE_MULTIPROCESSING, MP_NUM_CORES

        page_doc_response = ListDocIdsService().get(wiki_id)
        if page_doc_response['status'] != 200:
            return page_doc_response

        if USE_MULTIPROCESSING:
            m = Manager()
            d = m.dict()
            l = m.list()
            results = Pool(processes=MP_NUM_CORES).map(update_dict_wpdess, [(d, i, l) for i in page_doc_response[wiki_id]])
            entitySentiment = dict(d.items())
        else:
            entitySentiment = {}
            dss = WpDocumentEntitySentimentService()
            total = len(page_doc_response[wiki_id])
            counter = 0
            for doc_id in page_doc_response[wiki_id]:
                sent_response = dss.get_value(doc_id)
                if sent_response is not None:
                    print "%d / %d (%d keys)" % (counter, total, len(sent_response))
                    for key in sent_response:
                        entitySentiment[key] = entitySentiment.get(key, []) + sent_response[key]

        return {'status': 200, wiki_id: dict([(key, numpy.mean([i + 1 for i in entitySentiment[key]])-1) for key in entitySentiment])}



class WpDocumentEntitySentimentService(RestfulResource):

    """ Filters out sentiment in a document to only care about entities """
    @cached_service_request
    def get(self, doc_id):
        sentimentResponse = DocumentSentimentService().get(doc_id)
        if sentimentResponse['status'] is not 200:
            return sentimentResponse

        entities = WpEntitiesService().get_value(doc_id, [])

        return {'status': 200,
                doc_id: dict(filter(lambda x: title_confirmation.check_wp(x[0]) or x[0] in entities,
                                        sentimentResponse[doc_id]['averagePhraseSentiment'].items()))
                }

class AllEntitiesSentimentAndCountsService(RestfulResource):

    """ Key is entity name, and then dict of count and sentiment so we can sort and what not """
    @cached_service_request
    def get(self, wiki_id):
        counts = dict(
            WpWikiEntitiesService().get_value(wiki_id).items() +
            WikiEntitiesService().get_value(wiki_id).items()
        )
        sentiments = dict (
            WikiEntitySentimentService().get_value(wiki_id, {}).items() +
            WpWikiEntitySentimentService().get_value(wiki_id, {}).items()
        )

        resp_dict = {}
        for s in sentiments:
            resp_dict[s] = {'sentiment': sentiments[s] }

        for c in counts:
            for key in counts[c]:
                if key in resp_dict:
                    resp_dict[key]['count'] = c
                else:
                    resp_dict[key] = {'count': c}
            resp_dict[c] = dict(resp_dict.get(c, {}).items() + [('count', counts[c])])

        return { 'status': 200, wiki_id: resp_dict }
