__author__ = 'relwell'

from flask.ext import restful


class RestfulResource(restful.Resource):

    """
    Wraps restful.Resource to allow additional logic
    """

    def get_value(self, doc_id, backoff=None):
        """
        Allows us to call a service and extract data from its response
        :param doc_id: the id of the document
        :param backoff: default value
        :return: whatever the return value of the method call is
        """
        return self.get(doc_id).get(doc_id, backoff)


from . import caching
from . import document_access
from . import title_confirmation
from . import syntax
from . import discourse