from flask import Flask
from flask.ext import restful
from argparse import ArgumentParser
from ..caching import use_caching
from ..pooling import set_global_num_processes
from .. import discourse, document_access, syntax


def get_args():
    """
    Gets arguments from command line

    :return: argparse namespace
    :rtype: argparse.Namespace

    """
    ap = ArgumentParser()
    ap.add_argument('-x', '--no-cache', dest="cache", default=True, action="store_false")
    ap.add_argument('-w', '--write-only', dest="write_only", default=False, action="store_true")
    ap.add_argument('-r', '--read-only', dest="read_only", default=False, action="store_true")
    ap.add_argument('-n', '--no-compute', dest="no_compute", default=False, action="store_true")
    ap.add_argument('-p', '--processes', dest="processes", default=8, type=int)
    return ap.parse_args()


def register_resources(api):
    """
    Registers resources with the api

    :param api: the flask restful api class
    :type api: flask.ext.restful.api

    """
    api.add_resource(discourse.AllEntitiesSentimentAndCountsService,
                     '/Wiki/<string:wiki_id>/Entities/All/SentimentAndCounts')
    api.add_resource(discourse.entities.WikiEntitiesService,
                     '/Wiki/<string:wiki_id>/Entities/Wikia/Counts')
    api.add_resource(discourse.entities.WpWikiEntitiesService,
                     '/Wiki/<string:wiki_id>/Entities/Wikipedia/Counts')
    api.add_resource(discourse.entities.CombinedWikiEntitiesService,
                     '/Wiki/<string:wiki_id>/Entities/All/Counts')
    api.add_resource(discourse.entities.TopEntitiesService,
                     '/Wiki/<string:wiki_id>/Entities/Wikia/Top')
    api.add_resource(discourse.entities.WpTopEntitiesService,
                     '/Wiki/<string:wiki_id>/Entities/Wikipedia/Top')
    api.add_resource(discourse.entities.CombinedTopEntitiesService,
                     '/Wiki/<string:wiki_id>/Entities/All/Top')
    api.add_resource(discourse.entities.WikiPageEntitiesService,
                     '/Wiki/<string:wiki_id>/Pages/Entities/Wikia/Counts')
    api.add_resource(discourse.entities.WpWikiPageEntitiesService,
                     '/Wiki/<string:wiki_id>/Pages/Entities/Wikipedia/Counts')
    api.add_resource(discourse.entities.CombinedWikiPageEntitiesService,
                     '/Wiki/<string:wiki_id>/Pages/Entities/All/Counts')
    api.add_resource(discourse.entities.WikiPageToEntitiesService,
                     '/Wiki/<string:wiki_id>/Pages/Entities/Wikia')
    api.add_resource(discourse.entities.WpPageToEntitiesService,
                     '/Wiki/<string:wiki_id>/Pages/Entities/Wikipedia')
    api.add_resource(discourse.entities.CombinedPageToEntitiesService,
                     '/Wiki/<string:wiki_id>/Pages/Entities/All')
    api.add_resource(syntax.WikiToPageHeadsService,
                     '/Wiki/<string:wiki_id>/Pages/Heads')
    api.add_resource(syntax.HeadsCountService,
                     '/Wiki/<string:wiki_id>/Heads/Counts')
    api.add_resource(syntax.TopHeadsService,
                     '/Wiki/<string:wiki_id>/Heads/Top')
    api.add_resource(discourse.entities.EntityDocumentCountsService,
                     '/Wiki/<string:wiki_id>/Pages/Entities/Wikia/DocumentCounts')
    api.add_resource(discourse.entities.WpEntityDocumentCountsService,
                     '/Wiki/<string:wiki_id>/Pages/Entities/Wikipedia/DocumentCounts')
    api.add_resource(discourse.entities.CombinedDocumentEntityCountsService,
                     '/Wiki/<string:wiki_id>/Pages/Entities/All/DocumentCounts')
    api.add_resource(discourse.entities.EntitiesService,
                     '/Doc/<string:doc_id>/Entities/Wikia')
    api.add_resource(discourse.entities.WpEntitiesService,
                     '/Doc/<string:doc_id>/Entities/Wikipedia')
    api.add_resource(discourse.entities.CombinedEntitiesService,
                     '/Doc/<string:doc_id>/Entities/All')
    api.add_resource(discourse.entities.EntityCountsService,
                     '/Doc/<string:doc_id>/Entities/Wikia/Counts')
    api.add_resource(discourse.entities.WpEntityCountsService,
                     '/Doc/<string:doc_id>/Entities/Wikipedia/Counts')
    api.add_resource(discourse.entities.CombinedEntityCountsService,
                     '/Doc/<string:doc_id>/Entities/All/Counts')
    api.add_resource(discourse.sentiment.DocumentSentimentService,
                     '/Doc/<string:doc_id>/Sentiment')
    api.add_resource(discourse.sentiment.DocumentEntitySentimentService,
                     '/Doc/<string:doc_id>/Entities/All/Sentiment')
    api.add_resource(discourse.sentiment.WpDocumentEntitySentimentService,
                     '/Doc/<string:doc_id>/Entities/Wikipedia/Sentiment')
    api.add_resource(discourse.sentiment.WikiaDocumentEntitySentimentService,
                     '/Doc/<string:doc_id>/Entities/Wikia/Sentiment')
    api.add_resource(document_access.ParsedXmlService,
                     '/Doc/<string:doc_id>/XML')
    api.add_resource(syntax.AllNounPhrasesService,
                     '/Doc/<string:doc_id>/NPs')
    api.add_resource(syntax.AllVerbPhrasesService,
                     '/Doc/<string:doc_id>/VPs')
    api.add_resource(syntax.HeadsService,
                     '/Doc/<string:doc_id>/Heads')
    api.add_resource(discourse.entities.CoreferenceCountsService,
                     '/Doc/<string:doc_id>/CorefererenceCounts')


def get_app():
    """
    Access the app so we can hopefully get it working with uwsgi in another script

    :return: flask app
    :rtype: flask.Flask
    """
    args = get_args()
    if args.cache:
        use_caching(is_read_only=args.read_only, is_write_only=args.write_only, shouldnt_compute=args.no_compute)

    set_global_num_processes(args.processes)

    app = Flask(__name__)
    api = restful.Api(app)
    register_resources(api)
    return app


def main():
    """
    Main method, runs the app
    """
    get_app().run()


if __name__ == '__main__':
    main()