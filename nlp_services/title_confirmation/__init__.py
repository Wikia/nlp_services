"""
This submodule is used for referencing strings against data sources that connote entities
"""

from nltk.corpus import stopwords
import re

""" Memoization variables """
TITLES, REDIRECTS, CURRENT_WIKI_ID, USE_S3, WP_SEEN, ALL_WP, SQLITE_CONNECTION = [], {}, None, True, [], {}, None


def preprocess(title):
    """ Mutate each title to the appropriate pre-processed value
    :param row: cursor title
    :type row: str
    :return: the preprocessed title
    :rtype: str
    """
    stops = stopwords.words('english')
    return ' '.join(
        filter(lambda x: x not in stops,
               #500 chars should be plenty, todo fix unicode shit
               re.sub(' \(\w+\)', '', title.lower().replace('_', ' ')).split(' ')))[:500]
