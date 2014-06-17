"""
Responsible for re-caching titles and redirects for each wiki.
We upload these databases to S3 to enable Wikia entity cross-referencing.
"""

from argparse import ArgumentParser, Namespace
from multiprocessing import Pool
from ..caching import use_caching
from ..title_confirmation import AllTitlesService, RedirectsService
import requests


def get_args():
    """
    Gets the arguments from the command line

    :return: namespace
    :rtype: argparse.Namespace
    """

    ap = ArgumentParser(description="Re-primes the titles and redirects from all wikis with 50 or more articles")
    ap.add_argument('-p', '--processes', dest='processes', type=int, default=8)
    ap.add_argument('-r', '--refresh-cache', dest='refresh_cache', default=False, action='store_true')
    return ap.parse_args()


def prime_titles(args):
    """
    Invokes requisite service for titles

    :param args: argparse namespace with wiki_id added
    :type args: argparse.Namespace

    """
    use_caching(is_write_only=args.refresh_cache)
    AllTitlesService().get(args.wiki_id)
    RedirectsService().get(args.wiki_id)


def main():
    """
    Runs script
    """
    args = get_args()
    p = Pool(processes=args.processes)
    params = dict(q="lang_s: en AND articles_i:[50 TO *]", rows=500, start=0, wt='json')
    while True:
        print params['start']
        response = requests.get('http://search-s9:8983/solr/xwiki/select', params=params).json()
        p.map_async(prime_titles, [Namespace(wiki_id=doc['id'], **vars(args)) for doc in response['response']['docs']])
        if response['numFound'] <= params['start'] + params['rows']:
            break
        params['start'] += params['rows']


if __name__ == '__main__':
    main()