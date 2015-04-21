import sys
import argparse
import json
from pprint import pprint
from IPython.terminal import ipapp
from IPython.config.loader import Config

from solrcloudpy.connection import SolrConnection
from solrcloudpy.parameters import SearchOptions


def display_list(ob, pprinter, cycle):
    if len(ob) == 0:
        pprinter.text('[]')
        return

    e = ob[0]
    if type(e) == type({}):
        val = json.dumps(ob, indent=4)
        pprinter.text(val)
        return

    pprinter.text(str(ob))


def display_dict(ob, pprinter, cycle):
    try:
        val = json.dumps(ob, indent=4)
        pprinter.text(val)
    except TypeError:
        pprint(ob)


def get_config(args):
    c = Config()
    c.PromptManager.in_template = 'solr %s:%s> ' % (args.host, args.port)
    c.PromptManager.in2_template = 'solr %s:%s>' % (args.host, args.port)
    c.PromptManager.out_template = ''
    c.PromptManager.justify = False
    c.PlainTextFormatter.pprint = True
    c.TerminalInteractiveShell.confirm_exit = False
    return c


def get_conn(args):
    return SolrConnection(["%s:%s" % (args.host, args.port), ],
                          user=args.user,
                          password=args.password)


def main():
    parser = argparse.ArgumentParser(description='Parser for solrcloudpy console')
    parser.add_argument('--host', default='localhost', help='host')
    parser.add_argument('--port', default='8983', help='port')
    parser.add_argument('--user', default=None, help='user')
    parser.add_argument('--password', default=None, help='password')

    args = parser.parse_args(sys.argv[1:])

    conn = get_conn(args)
    c = get_config(args)

    banner = "SolrCloud Console\nUse the 'conn' object to access a collection"
    banner2 = "\nType 'collections' to see the list of available collections"

    app = ipapp.TerminalIPythonApp.instance()
    shell = ipapp.TerminalInteractiveShell.instance(
        parent=app,
        profile_dir=app.profile_dir,
        ipython_dir=app.ipython_dir,
        user_ns={"conn": conn,
                 "collections": conn.list(),
                 "SearchOptions": SearchOptions},
        banner1=banner,
        banner2=banner2,
        display_banner=False,
        config=c)

    formatter = shell.get_ipython().display_formatter.formatters["text/plain"]
    formatter.for_type(type([]), display_list)
    formatter.for_type(type({}), display_dict)

    shell.configurables.append(app)
    app.shell = shell
    app.initialize(argv=[])
    app.start()
    return
