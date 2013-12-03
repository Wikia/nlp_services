"""
This submodule is used for referencing strings against data sources that connote entities
"""

from nltk.corpus import stopwords
import re

""" Memoization variables """
USE_WIKIPEDIA = True


def preprocess(title):
    """
    Mutate each title to the appropriate pre-processed value
    :param title: cursor title
    :type title: str
    :return: the preprocessed title
    :rtype: str
    """
    stops = stopwords.words('english')
    return ' '.join(
        filter(lambda x: x not in stops,
               #500 chars should be plenty, todo fix unicode shit
               re.sub(' \(\w+\)', '', title.lower().replace('_', ' ')).split(' ')))[:500]

from wikia import AllTitlesService
from wikipedia import check_wp

def confirm(title, wiki_id=None, use_wikipedia=None):
    """
    Uses one or more methods for determining whether the title is an entity
    An entity is defined here as being germane to the scope of the universe of discourse
    The universe of discourse here is either wikipedia titles or titles in a given wiki
    :param title: the candidate entity
    :type title: str
    :param use_wikipedia: whether to reference a wiki
    :type use_wikipedia: bool
    """
    global USE_WIKIPEDIA
    use_wikipedia = USE_WIKIPEDIA if use_wikipedia is None else use_wikipedia
    can_confirm = False
    if wiki_id is not None:
        can_confirm = preprocess(title) in wikia.AllTitlesService().get_value(wiki_id, [])
    if not can_confirm and use_wikipedia:
        can_confirm = wikipedia.check_wp(title)
    return can_confirm


def canonical(title, wiki_id):
    """
    Returns the title itself, or the title which it redirects to
    :param title: the candidate title string
    :type title: str
    :param wiki_id: the id of the wiki
    :type wiki_id: str|int
    :return: The canonical title
    :rtype: str
    """
    redirects = wikia.RedirectsService().get_value(wiki_id)
    return redirects.get(preprocess(title), title)
