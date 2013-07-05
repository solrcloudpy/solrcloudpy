solrcloudpy
===========

solrcloudpy is a python library for interacting with SolrCloud. This library aims to take advantage of the following features of Solr:

* Distributed indexing and searching and transparent failover
* Full JSON api
* Centralized index management
* Near-realtime search

The API is mean to be close to pymongo's API, where one can access collections and databases as simple attributes 

Usage
-------

Example usage:

     >>> conn = HTTPConnection(["localhost:9983","localhost:8984"])
     >>> collection = collection.Collection(conn)
     >>> collection.create('test1')
     >>> print collection.test1.search(q='')
     ...

 
