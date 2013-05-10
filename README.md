solrcloudpy
===========

solrcloudpy is a python library for interacting with Solr 4. This library aims to take advantage of the following features of Solr:

* Distributed indexing and searching and transparent failover
* Full JSON api
* Centralized index management
* Near-realtime search

The API is mean to be close to pymongo's API, wher eone cann access collections and databases as attributes 
Usage
-------
Solr uses Zookeeper for distributed capabilities, so we will take advantage of that to:

* detect live nodes, 
* remove failing nodes
* find cluster health

Example usage:

     >>> zk = ZConnection("localhost:9983")
     >>> collection = collection.Collection
     >>> collection.create('test1')
     >>> print collection.test1.search(q='')
     ...

 