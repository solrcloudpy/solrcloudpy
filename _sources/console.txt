Using the console
=================

``solrcloudpy`` comes with a console that can be run simply by typing
``solrconsole``. It has a few convenniences, such as an already-created
:class:`~solrcloudpy.connection.SolrConnection` object and :class:`~solrcloudpy.parameters.SearchOptions` that can be referred to directly. 


::

     $ solrconsole --host=localhost --port=8983 
     SolrCloud Console
     Use the 'conn' object to access a collection

     Type 'collections' to see the list of available collections
     solr localhost:8983> conn.collection1.search(SearchOptions.commonparameters.q("junk"))
     {   
         "response": "SolrResponse << {'start': 0, 'numFound': 0, 'docs': []} >>"
     }

     solr localhost:8983> res.response
     {
         "start": 0, 
         "numFound": 0, 
         "docs": []
     }

Usage:

::

    usage: solrconsole [-h] [--host HOST] [--port PORT] [--user USER]
                   [--password PASSWORD]

    Parser for solrcloudpy console

    optional arguments:
    -h, --help           show this help message and exit
    --host HOST          host
    --port PORT          port
    --user USER          user
    --password PASSWORD  password
