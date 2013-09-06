solrcloudpy
===========

solrcloudpy is a python library for interacting with SolrCloud. This library aims to take advantage of the following features of Solr:

* Distributed indexing and searching and transparent failover
* Full JSON api
* Centralized index management
* Near-realtime search

The API is mean to be close to pymongo's API, where one can access collections and databases as simple attributes 
or dictionary keys.  

Usage
-------
.. code-block:: python

     from solrcloudpy.connection import HTTPConnection
     from solrcloudpy.collection import Collection 
   
     conn = HTTPConnection(["localhost:9983","localhost:8984"])
     collection = Collection(conn)
     collection.create('test1',num_shards=1,replication_factor=2)
          
     # Indexing documents
     docs = [{"id":"1", "name":"a"},{"id":"2","name":"b"}]
     collection.test1.add(docs)

     # Searching documents
     print collection.test1.search(q='*:*')
 
