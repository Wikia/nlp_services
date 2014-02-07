"""
This module contains various Wikia utilities.
"""
import json
import os
import requests

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
