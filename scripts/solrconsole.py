import sys
import argparse
from solrcloudpy.connection import HTTPConnection

def main():
    parser = argparse.ArgumentParser(description='Parser for solrcloudpy console')
    parser.add_argument('--host', default='localhost',
                        help='host')
    parser.add_argument('--port', default='8983',
                        help='port')
    args = parser.parse_args(sys.argv[1:])

    def configure(host,port):
        return HTTPConnection(["%s:%s"%(host,port),])

    conn = configure(args.host,args.port)

    ########
    from IPython.config.loader import Config
    c = Config()
    c.PromptManager.in_template = 'solr %s:%s> ' % (args.host,args.port)
    c.PromptManager.in2_template = 'solr %s:%s>' % (args.host,args.port)
    c.PromptManager.out_template = ''
    c.PromptManager.justify = False
    c.PlainTextFormatter.pprint = True
    c.TerminalInteractiveShell.confirm_exit = False

    banner = "SolrCloud Console\n"

    colls = ", ".join(conn.list())
    banner2 = "\nType 'collections' to see the list of available collections"

    from IPython.terminal import ipapp
    app = ipapp.TerminalIPythonApp.instance()
    shell = ipapp.TerminalInteractiveShell.instance(
        parent=app,
        profile_dir=app.profile_dir,
        ipython_dir=app.ipython_dir,
        user_ns={"conn":conn,"collections":conn.list()},
        banner1=banner,
        banner2=banner2,
        #banner=banner,
        display_banner=False,
        config=c)
    shell.configurables.append(app)
    app.shell = shell
    # shell has already been initialized, so we have to monkeypatch
    # app.init_shell() to act as no-op
    #app.init_shell = lambda: None
    app.initialize(argv=[])
    app.start()
    return

