"""
This module contains various Wikia utilities.
"""
import json
import os
import requests
from .. import RestfulResource

# Get absolute path
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# Load serialized hostnames into memory
with open(os.path.join(BASE_PATH, 'data/hostnames.json')) as f:
    hostnames = json.loads(f.read())

class TopArticlesService(RestfulResource):
    """Get top n articles for a given wiki"""

    def __init__(self, n=50):
        """Constructor; optionally define how many articles to return"""
        self.n = n

    def get(self, wiki_id):
        """Return full IDs of the top n articles for a given wiki ID
        :param wiki_id: string, ID of the wiki in Solr"""
        hostname = hostnames.get(wiki_id, 0)
        if hostname:
            items = requests.get('http://' + hostname + '/api/v1/Articles/List?limit=%d' % self.n).json()
            articles = ['%s_%i' % (wiki_id, item.get('id')) for item in items.get('items', [])]
            return articles
        return []
