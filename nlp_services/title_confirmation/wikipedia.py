"""
Interacts with a sqlite database of wikipedia titles for entity confirmation
"""
from gzip import open as gzopen
import os
import sqlite3 as lite
from nlp_services.title_confirmation import preprocess


"""
Memoization variables
"""
WP_SEEN = []
SQLITE_CONNECTION = None


def check_wp(title):
    """
    Checks if a "title" is a title in wikipedia first using memoization cache, then check_wp_s3

    :param title: the title string
    :type title: str

    :return: whether the string is a title in wikipedia
    :rtype: bool

    """
    global WP_SEEN
    ppt = preprocess(title)
    return ppt in WP_SEEN or check_wp_sqlite(ppt)


def check_wp_sqlite(title):
    """
    Queries the title against the sqlite db and then memoizes it into the WP_SEEN variable for performance

    :param title: the title string
    :type title: str

    :return: whether the title is legit
    :rtype: bool

    """
    global WP_SEEN
    cursor = get_sqlite_connection().cursor()
    cursor.execute("SELECT * FROM `titles` where `title` = \"%s\"" % (title.replace('"', '""')))
    if cursor.fetchone() is not None:
        WP_SEEN.append(title)
        return True
    return False


def get_sqlite_connection():
    """
    Memoizes sqlite connection

    :return: sqlite connection
    :rtype: sqlite3.Connection

    """
    global SQLITE_CONNECTION
    if SQLITE_CONNECTION is None:
        SQLITE_CONNECTION = bootstrap_sqlite_connection()
    return SQLITE_CONNECTION


def bootstrap_sqlite_connection():
    """
    Gets the sqlite connection, validating that it is well-formed first

    :return: sqlite connection
    :rtype: sqlite3.Connection

    """
    candidate_paths = map(lambda x: x+'/wp_titles.db',
                          [os.path.dirname(os.path.realpath(__file__)),
                           os.path.expanduser("~"),
                           os.getcwd()])

    db_paths = filter(os.path.exists, candidate_paths)

    if len(db_paths) == 0:
        raise LookupError("The wp_titles.db file can't be found. "
                          "Please add it to the nlp_services.title_confirmation folder or your home directory.")
    conn = lite.connect(db_paths[-1])
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='titles'")
    if cursor.fetchone() is None:
        raise LookupError("The wp_titles.db instance doesn't have the right table."
                          "Please make sure you downloaded the wp_titles.db file from somewhere legit.")
    return conn


def create_wp_table(conn):
    """
    Creates the wp table from a sqlite connection. This is basically here for posterity, shouldn't be used.

    :param conn: a sqlite connection
    :type conn: sqlite3.Connection

    """
    print 'creating'
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS `titles`
                    (title TEXT UNIQUE);''')

    print "Extracting/Inserting..."
    counter = 0
    for line in list(set(map(lambda x: preprocess(x.strip()),
                             gzopen('/'.join(os.path.realpath(__file__).split('/')[:-1])
                                     + '/enwiki-20131001-all-titles-in-ns0.gz')))):
        cur.execute("INSERT INTO `titles` (`title`) VALUES (?)", (line,))
        counter += 1
        if counter % 500 == 0:
            print counter

    print "Committing..."
    conn.commit()
