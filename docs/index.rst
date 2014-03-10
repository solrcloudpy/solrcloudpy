.. solrcloudpy documentation master file, created by
   sphinx-quickstart on Sat Mar  8 02:18:25 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Solrcloudpy
===========

``solrcloudpy`` is a python library for interacting with SolrCloud. This library aims to take advantage of the following features of Solr:

* Distributed indexing and searching and transparent failover
* Full JSON api
* Centralized index management
* Near-realtime search

The API is meant to be close to ``pymongo`` 's API, where one can access collections as simple attributes or dictionary keys.  

::

     >>> conn = HTTPConnection(["localhost:9983","localhost:8984"])
     >>> collection = Collection('test1',conn)
     >>> collection.create('test1',num_shards=1,replication_factor=2)
     
     # Access an existing collection
     >>> conn.test_collection.search(q='query')
     {   
         "response": "DictObject << {'start': 0, 'numFound': 0, 'docs': []} >>"
     }
     >>> conn["test_collection"].search(q='query 2')
     {   
         "response": "DictObject << {'start': 0, 'numFound': 0, 'docs': []} >>"
     }


``solrcloudpy`` comes with a console that can be run simply by typing ``solrconsole``

::

     $ solrconsole --host=localhost --port=8983 
     SolrCloud Console
     Use the 'conn' object to access a collection

     Type 'collections' to see the list of available collections
     solr localhost:8983> conn.collection1.search('sd')
     {   
         "response": "DictObject << {'start': 0, 'numFound': 0, 'docs': []} >>"
     }

     solr localhost:8983> res.response
     {
         "start": 0, 
         "numFound": 0, 
         "docs": []
     }



API documentation
-----------------

.. toctree::
   :maxdepth: 2

   apidocs/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

