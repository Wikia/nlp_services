"""
Responsible for pulling down data from AWS
"""

from corenlp_xml.document import Document

from boto import connect_s3
from boto.s3.key import Key
from .. import RestfulResource
from ..caching import cached_service_request


S3_BUCKET = None


def get_s3_bucket():
    """
    Accesses an S3 connection for us, memoized
    :return: s3 connection
    :rtype:class:`boto.s3.connection.S3Connection`
    """
    global S3_BUCKET
    if S3_BUCKET is None:
        S3_BUCKET = connect_s3().get_bucket('nlp-data')
    return S3_BUCKET


def get_document_by_id(doc_id):
    service_response = ParsedXmlService().get(doc_id)
    document = None
    if service_response.get('status') == 200:
        document = Document(service_response[doc_id])
    return document


class ParsedXmlService(RestfulResource):

    """ Read-only service responsible for accessing XML from FS """
    def get(self, doc_id):
        """ Right now just points to new s3 method, just didn't want to remove the old logic just yet.
        :param doc_id: the doc id
        :return: a JSON response
        """
        return self.get_from_s3(doc_id)

    def get_from_s3(self, doc_id):
        """ Returns a response with the XML of the parsed text
        :param doc_id: the id of the document in Solr
        :return: json response
        :rtype: dict
        """
        try:
            bucket = get_s3_bucket()
            key = Key(bucket)
            key.key = 'xml/%s/%s.xml' % tuple(doc_id.split('_'))

            if key.exists():
                response = {'status': 200, doc_id: key.get_contents_as_string()}
            else:
                response = {'status': 500, 'message': 'Key does not exist'}
            return response
        except socket.error:
            # probably need to refresh our connection
            global S3_BUCKET
            S3_BUCKET = None
            return self.get_from_s3(doc_id)


class ListDocIdsService(RestfulResource):

    """ Service to expose resources in WikiDocumentIterator """
    @cached_service_request
    def get(self, wiki_id, start=0, limit=None):

        bucket = get_s3_bucket()
        keys = bucket.get_all_keys(prefix='xml/%s/' % (str(wiki_id)), max_keys=1)
        if len(keys) == 0:
            return {'status': 500, 'message': 'Wiki not yet processed'}

        if limit:
            ids = ArticleDocIdIterator(wiki_id)[start:limit]
        else:
            ids = [doc_id for doc_id in ArticleDocIdIterator(wiki_id)[start:]]
        return {wiki_id: ids, 'status': 200, 'numFound': len(ids)}


class ArticleDocIdIterator:

    """ Get all existing document IDs for a wiki -- not a service """

    def __init__(self, wid):
        """ Constructor method
        :param wid: the wiki ID we want to iterate over
        """
        bucket = get_s3_bucket()
        self.wid = wid
        self.counter = 0

        def id_from_key(x):
            split = x.split('/')
            return "%s_%s" % (split[-2], split[-1].replace('.xml', ''))
        self.keys = [id_from_key(key.key) for key in bucket.list(prefix='xml/'+str(wid)+'/') if key.key.endswith('.xml')]

    def __iter__(self):
        """ Iterator method """
        return self.next()

    def __getitem__(self, index):
        """ Allows array access
        :param index: int value of index
        """
        return self.keys[index]

    def next(self):
        """ Get next article ID """
        if self.counter == len(self.keys):
            raise StopIteration
        self.counter += 1
        return self.keys[self.counter-1]