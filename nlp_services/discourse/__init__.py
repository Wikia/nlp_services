__author__ = 'relwell'

from .. import RestfulResource
from ..caching import cached_service_request
import entities
import sentiment


class AllEntitiesSentimentAndCountsService(RestfulResource):

    @cached_service_request
    def get(self, wiki_id):
        """
        Returns a dictionary of entities to their count and sentiment for the wiki
        Key is entity name, and then dict of count and sentiment so we can sort
        and what not

        :param wiki_id: the ID of the wiki
        :type wiki_id: str|int

        :return: a dictionary of entities to count and sentiment for the wiki
        :rtype: dict

        """
        wiki_id = str(wiki_id)
        counts = dict(
            entities.WpWikiEntitiesService().get_value(
                wiki_id, {}).items() +
            entities.WikiEntitiesService().get_value(
                wiki_id, {}).items()
            )
        sentiments = dict(
            sentiment.WikiEntitySentimentService().get_value(
                wiki_id, {}).items() +
            sentiment.WpWikiEntitySentimentService().get_value(
                wiki_id, {}).items()
            )

        resp_dict = {}
        for s in sentiments:
            resp_dict[s] = {'sentiment': sentiments[s]}

        for c in counts:
            for key in counts[c]:
                if key in resp_dict:
                    resp_dict[key]['count'] = c
                else:
                    resp_dict[key] = {'count': c}
            resp_dict[c] = dict(resp_dict.get(c, {}).items() + [('count', counts[c])])

        return {'status': 200, wiki_id: resp_dict}
