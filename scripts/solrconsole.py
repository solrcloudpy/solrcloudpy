import sys
import argparse
import json
from pprint import pprint
from IPython.terminal import ipapp
from IPython.config.loader import Config

from solrcloudpy.connection import HTTPConnection
from solrcloudpy.parameters import  Params

def display_list(ob, pprinter, cycle):
    if len(ob) == 0 :
        ppprinter.text('[]')
        return

    e = ob[0]
    if type(e) == type({}):
        val = json.dumps(ob,indent=4)
        pprinter.text(val)
        return

    pprinter.text(ob)

def display_dict(ob, pprinter, cycle):
    try:
        val = json.dumps(ob,indent=4)
        pprinter.text(val)
    except TypeError:
        pprint(ob)
        
def get_config(args):
    c = Config()
    c.PromptManager.in_template = 'solr %s:%s> ' % (args.host,args.port)
    c.PromptManager.in2_template = 'solr %s:%s>' % (args.host,args.port)
    c.PromptManager.out_template = ''
    c.PromptManager.justify = False
    c.PlainTextFormatter.pprint = True
    c.TerminalInteractiveShell.confirm_exit = False
    return c

def get_conn(host,port):
    return HTTPConnection(["%s:%s"%(host,port),])

def main():
    parser = argparse.ArgumentParser(description='Parser for solrcloudpy console')
    parser.add_argument('--host', default='localhost',help='host')
    parser.add_argument('--port', default='8983',help='port')
    args = parser.parse_args(sys.argv[1:])

    conn = get_conn(args.host,args.port)
    c = get_config(args)

    banner = "SolrCloud Console\nUse the 'conn' object to access a collection"
    banner2 = "\nType 'collections' to see the list of available collections"

    app = ipapp.TerminalIPythonApp.instance()
    shell = ipapp.TerminalInteractiveShell.instance(
        parent=app,
        profile_dir=app.profile_dir,
        ipython_dir=app.ipython_dir,
        user_ns={"conn":conn,
                 "collections":conn.list(),
                 "Params":Params},
        banner1=banner,
        banner2=banner2,
        #banner=banner,
        display_banner=False,
        config=c)

    formatter = shell.get_ipython().display_formatter.formatters["text/plain"]
    formatter.for_type(type([]),display_list)
    formatter.for_type(type({}),display_dict)

    shell.configurables.append(app)
    app.shell = shell
    # shell has already been initialized, so we have to monkeypatch
    # app.init_shell() to act as no-op
    #app.init_shell = lambda: None
    app.initialize(argv=[])
    app.start()
    return
