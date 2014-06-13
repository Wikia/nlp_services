from ..pooling import pool
from ..discourse.entities import es_get
from ..document_access import ListDocIdsService
from ..caching import use_caching
import argparse


def get_args():
    """
    Defines command-line arguments for this script

    :return: argparse namespace
    :rtype: argparse.Namespace

    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki-id", dest="wiki_id")
    ap.add_argument("--num-processes", dest="num_processes", default=8, type=int)
    ap.add_argument("--percentage-pages", dest="percentage_pages", default=10, type=float)
    ap.add_argument("--slice", dest="slice", default=0, type=int)
    ap.add_argument("--no-caching", dest="no_caching", default=False, action="store_true")
    return ap.parse_args()


def main():
    """
    Main method, responsible for caching entities in a distributed fashion.
    """
    args = get_args()
    if not args.no_caching:
        use_caching(is_write_only=True)
    all_pages = ListDocIdsService().get_value(args.wiki_id)
    slice_size = int(len(all_pages) * (args.percentage_pages * .01))
    slice_start = range(0, len(all_pages), int(slice_size))[args.slice]
    my_pages = all_pages[slice_start:slice_start+slice_size]
    print "Working on", slice_size, "pages"
    print pool(num_processes=args.num_processes).map_async(es_get, my_pages).get()


if __name__ == "__main__":
    main()
