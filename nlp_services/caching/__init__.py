"""
Caching library -- basically memoizes stuff for now
"""
from boto import connect_s3
import json

"""
If this value gets initialized then we will start memoizing things with S3
"""
CACHE_BUCKET = None

WRITE_ONLY = False
READ_ONLY = False
DONT_COMPUTE = False
PER_SERVICE_CACHING = {}


def bucket(new_bucket = None):
    """ Access & mutate so we don't have globals in every function
    :param new_bucket:s3 bucket
    :return
    """
    global CACHE_BUCKET
    if new_bucket:
        CACHE_BUCKET = new_bucket
    return CACHE_BUCKET


def read_only(mutate = None):
    """ Access & mutate so we don't need globals in every function
    :param mutate: a boolean value
    """
    global READ_ONLY
    if mutate is not None:
        READ_ONLY = mutate
    return READ_ONLY


def write_only(mutate = None):
    """ Access & mutate so we don't need globals in every function
    :param mutate: a boolean value
    """
    global WRITE_ONLY
    if mutate is not None:
        WRITE_ONLY = mutate
    return WRITE_ONLY


def dont_compute(mutate=None):
    """ With read only, will prevent calling method
    :param mutate: a boolean val
    """
    global DONT_COMPUTE
    if mutate is not None:
        DONT_COMPUTE = mutate
    return DONT_COMPUTE


def per_service_caching(services=None):
    """ Store a dict of per-service cache options.
    :param services: a dict of the following structure:
                     { service_name : { 'read_only': True, 'write_only': False, 'dont_compute': False } }
                     -- if these values aren't set, the default is the globally set value
    """
    global PER_SERVICE_CACHING
    if services is not None:
        PER_SERVICE_CACHING = services
    return PER_SERVICE_CACHING


def use_caching(is_write_only=False, is_read_only=False, shouldnt_compute=False, per_service_cache={}):
    """ Invoke this to set CACHE_BUCKET and enable caching on these services 
    :param is_write_only: whether we should avoid reading from the cache
    :param is_read_only: whether we should avoid writing to the cache
    :param per_service_cache: dict that relates specific how specific services should be cached
    """
    bucket(connect_s3().get_bucket('nlp-data'))
    read_only(is_read_only)
    write_only(is_write_only)
    dont_compute(shouldnt_compute)
    per_service_caching(per_service_cache)


def purge_for_doc(doc_id):
    """ Remove all service responses for a given doc id
    :param doc_id: the document id. if it's a wiki id, you're basically removing all wiki-scoped caching
    :return: a MultiDeleteResult
    """
    b = bucket()
    prefix = 'service_responses/%s' % doc_id.replace('_', '/')
    return b.delete_keys([key for key in b.list(prefix=prefix)])
    

def purge_for_wiki(wiki_id):
    """ Remove cached service responses for a given wiki id
    :param wiki_id: the id of the wiki
    :return: a MultiDeleteResult
    """
    b = bucket()
    prefix = 'service_responses/%s' % wiki_id
    return b.delete_keys([key for key in b.list(prefix=prefix)])


def cached_service_request(get_method):
    """ This is a decorator responsible for optionally memoizing a service response into the cache
    :param get_method: the function we're wrapping -- should be a GET endpoint
    """
    def invoke(self, *args, **kw):

        b = bucket()
        if b is None:
            response = get_method(self, *args, **kw)

        else:
            doc_id = kw.get('doc_id', kw.get('wiki_id', None))
            if not doc_id:
                doc_id = args[0]
            service = str(self.__class__.__name__)+'.'+get_method.func_name
            path = 'service_responses/%s/%s' % (doc_id.replace('_', '/'), service)
            
            result = None
            if not per_service_caching().get(service, {}).get('write_only', write_only()):
                result = b.get_key(path)

            if result is None and not per_service_caching().get(service, {}).get('dont_compute', dont_compute()):
                response = get_method(self, *args, **kw)

                if response.get('status', 500) == 200 \
                        and not per_service_caching().get(service, {}).get('read_only', read_only()):
                    key = b.new_key(key_name=path)
                    print "got ", service, doc_id
                    key.set_contents_from_string(json.dumps(response, ensure_ascii=False))
            elif result is None and per_service_caching().get(service, {}).get('dont_compute', dont_compute()):
                return {'status': 404, doc_id: {}}
            else:
                try:
                    response = json.loads(result.get_contents_as_string())
                except:
                    response = get_method(self, *args, **kw)
                    if response['status'] == 200 \
                            and not per_service_caching().get(service, {}).get('read_only', read_only()):
                        key = b.new_key(key_name=path)
                        key.set_contents_from_string(json.dumps(response, ensure_ascii=False))

        return response
    return invoke
