from flask import Flask
from flask.ext import restful
from argparse import ArgumentParser
from .caching import use_caching
from .pooling import set_global_num_processes


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
    api.add_resource()


def main():
    """
    Main method, runs the app
    """
    args = get_args()
    if args.cache:
        use_caching(is_read_only=args.read_only, is_write_only=args.write_only, shouldnt_compute=args.no_compute)

    set_global_num_processes(args.processes)

    app = Flask(__name__)
    api = restful.api(app)
    register_resources(api)
    app.run()


if __name__ == '__main__':
    main()