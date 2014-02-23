solrcloudpy
===========

`solrcloudpy` is a python library for interacting with SolrCloud. This library aims to take advantage of the following features of Solr:

* Distributed indexing and searching and transparent failover
* Full JSON api
* Centralized index management
* Near-realtime search

The API is mean to be close to pymongo's API, where one can access collections as simple attributes 
or dictionary keys.  

Usage
-------
.. code-block:: python

     from solrcloudpy.connection import HTTPConnection
     from solrcloudpy.collection import Collection 
   
     # create a collection
     conn = HTTPConnection(["localhost:9983","localhost:8984"])
     collection = Collection(conn)
     collection.create('test1',num_shards=1,replication_factor=2)
     
     # Access an existing collection
     conn.test_collection.search(q='query')
     conn["test_collection"].search(q='query 2')
     
     # Indexing documents
     docs = [{"id":"1", "name":"a"},{"id":"2","name":"b"}]
     collection.add(docs)

     # Searching documents
     print collection.search(q='*:*')
 
     
Console
-------
`solrcloudpy` comes with a console that can be run simply by typing `solrconsole`

.. code-block::

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

