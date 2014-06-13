try:
    from wikicities.DB import LoadBalancer
except:
    pass  #screw it

from gzip import GzipFile
from StringIO import StringIO
from boto import connect_s3
from nlp_services.title_confirmation import preprocess
from nlp_services import RestfulResource
from nlp_services.caching import cached_service_request
import phpserialize
import json

# memoization variables
TITLES = []
REDIRECTS = {}
CURRENT_WIKI_ID = None
USE_S3 = True


# todo: this is probably bad
yml = '/usr/wikia/conf/current/DB.yml'


def get_config():
    return yml


def get_global_db(master=False):
    """
    Accesses the wikia global db

    :param master: whether we should use the writeable master db
    :type master: bool

    :return: database connection
    :rtype: MySQLdb.connections.Connection

    """
    lb = LoadBalancer(get_config())
    return lb.get_db_by_name('wikicities', master=master)


def get_local_db_from_wiki_id(wiki_id, master=False):
    """
    Accesses a given wiki's database

    :param wiki_id: the id of the wiki in the wikicities db
    :type wiki_id: int|str
    :param master: whether to use the writeable master
    :type master: bool

    :return: database connection
    :rtype: MySQLdb.connections.Connection

    """
    global CURRENT_WIKI_ID
    cursor = get_global_db().cursor()
    sql = "SELECT city_id, city_dbname FROM city_list WHERE city_id = %s" % str(wiki_id)
    cursor.execute(sql)
    result = cursor.fetchone()
    if not result:
        raise ValueError("No wiki found")

    CURRENT_WIKI_ID = result[0]
    return LoadBalancer(get_config()).get_db_by_name(result[1], master=master)


def get_namespaces(global_db, wiki_id):
    """ Accesses the default content namespaces for the wiki

    :param global_db: the global database object
    :type global_db: MySQLdb.connections.Connection

    :return: list of content namespacs
    :rtype: list

    """
    cursor = global_db.cursor()
    cursor.execute("SELECT cv_value FROM city_variables WHERE cv_city_id = %s AND cv_variable_id = 359" % str(wiki_id))
    result = cursor.fetchone()
    return phpserialize.loads(result[0]).values() if result else [0, 14]


def get_titles_for_wiki_id(wiki_id):
    """
    Accesses all titles for a given wiki_id
    TODO: a sqlite db in s3 for every title database??

    :param wiki_id: the id of the wiki
    :type wiki_id: int|str

    :return: list of all title strings
    :rtype: list

    """
    global TITLES, CURRENT_WIKI_ID, USE_S3
    if wiki_id == CURRENT_WIKI_ID and len(TITLES) > 0:
        return TITLES

    if USE_S3:
        bucket = connect_s3().get_bucket('nlp-data')
        key = bucket.get_key('article_titles/%s.gz' % str(wiki_id))
        if key is not None:
            io = StringIO()
            key.get_file(io)
            io.seek(0)
            stringdata = GzipFile(fileobj=io, mode='r').read().decode('ISO-8859-2').encode('utf-8')
            TITLES = json.loads(stringdata)[wiki_id]
        else:
            # throw an error maybe?
            TITLES = []
    else:
        local_db = get_local_db_from_wiki_id(get_global_db(), wiki_id)
        CURRENT_WIKI_ID = wiki_id
        cursor = local_db.cursor()
        cursor.execute("SELECT page_title FROM page WHERE page_namespace IN (%s)" % ", ".join(map(str, get_namespaces(get_global_db(), wiki_id))))
        TITLES = set(map(lambda x: preprocess(x[0]), cursor))

    CURRENT_WIKI_ID = wiki_id
    return TITLES


def get_redirects_for_wiki_id(wiki_id):
    """
    Returns all redirects for the provided wiki ID
    TODO: per-wiki sqlite db in s3?

    :param wiki_id: the wiki_id in question
    :type wiki_id: int|str

    :return: list of redirect strings
    :rtype: list

    """
    global REDIRECTS, CURRENT_WIKI_ID, USE_S3
    if wiki_id == CURRENT_WIKI_ID and len(REDIRECTS) > 0:
        return REDIRECTS

    if USE_S3:
        bucket = connect_s3().get_bucket('nlp-data')
        key = bucket.get_key('article_redirects/%s.gz' % str(wiki_id))
        if key is not None:
            io = StringIO()
            key.get_file(io)
            io.seek(0)
            stringdata = GzipFile(fileobj=io, mode='r').read()
            REDIRECTS = json.loads(stringdata)[wiki_id]
        else:
            # should check on this
            REDIRECTS = {}
    else:
        local_db = get_local_db_from_wiki_id(get_global_db(), wiki_id)
        cursor = local_db.cursor()
        cursor.execute("SELECT page_title, rd_title FROM redirect INNER JOIN page ON page_id = rd_from")
        REDIRECTS = dict([map(preprocess, row) for row in cursor])

    CURRENT_WIKI_ID = wiki_id
    return REDIRECTS


class AllTitlesService(RestfulResource):

    """ Responsible for accessing all titles from database using title_confirmation module """

    @cached_service_request
    def get(self, wiki_id):
        """ Extracts titles for a wiki from database
        The module it uses stores this value memory when caching is off.

        :param wiki_id: the id of the wiki
        :type wiki_id: str|int

        :return: response
        :rtype: dict
        """
        return {'status': 200, wiki_id: list(get_titles_for_wiki_id(str(wiki_id)))}


class RedirectsService(RestfulResource):

    """ Responsible for accessing list of redirects, correlating to their canonical title """
    @cached_service_request
    def get(self, wiki_id):
        """ Gives us a dictionary of redirect to canonical title
        In-memory caching when we don't have db caching.

        :param wiki_id: the id of the wiki
        :type wiki_id: int|str

        :return: response
        :rtype: dict
        """
        return {'status': 200, wiki_id: get_redirects_for_wiki_id(str(wiki_id))}
