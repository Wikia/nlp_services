"""
This module contains various Wikia utilities.
"""

import os.path
import requests
from corenlp_xml.document import Document
from ..syntax import get_pos_leaves, get_pos_phrases

NOUN_TAGS = [u'NP', u'NN', u'NNS', u'NNP', u'NNPS']


def get_top_articles(wiki_id, n=50):
    """Get top n articles for a given wiki ID
    :param wiki_id: string, ID of the wiki in Solr
    :param n: int, number of articles to return
    :return: list of article ID strings"""
    articles = []
    hostname = requests.get('http://www.wikia.com/api/v1/Wikis/Details', params={'ids': wiki_id}).json().get('items', {}).get(wiki_id, {}).get('url')
    if hostname:
        items = requests.get(hostname + 'api/v1/Articles/List?limit=%d' % n).json()
        articles = ['%s_%i' % (wiki_id, item.get('id')) for item in items.get('items', [])]
    return articles


def main_page_nps(wiki_id):
    """
    Find all noun phrases on a wiki's main page.

    :type wiki_id: string
    :param wiki_id: The wiki ID to extract NPs from

    :rtype: list
    :return: A list of NPs extracted from the main page of the specified wiki
    """
    response = requests.get(
        'http://search-s10:8983/solr/main/select',
        params=dict(q='wid:%s AND is_main_page:true' % wiki_id, fl='id',
                    wt='json'))

    docs = response.json().get('response', {}).get('docs', [{}])
    if not docs:
        return []
    doc_id = docs[0].get('id', None)

    return get_pos_phrases(doc_id, NOUN_TAGS)


def phrases_for_wiki_field(wiki_id, field):
    """
    Find all noun phrases in a locally-cached parse of a particular Solr field
    for a wiki.

    :type wiki_id: string
    :param wiki_id: The wiki ID to extract NPs from

    :type field: string
    :param field: The name of the Solr field to extract NPs from

    :rtype: list
    :return: A list of NPs in the given field for the wiki specified
    """
    path = '/data/wiki_xml/%s/%s.xml' % (wiki_id, field)
    if not os.path.exists(path):
        return []

    text = open(path, 'r').read()
    if len(text) > 0:
        document = Document(text)
        return get_pos_leaves(document, NOUN_TAGS)

    return []
