solrcloudpy
===========

solrcloudpy is a python library for interacting with Solr 4. This library aims to take advantage of the following features of Solr:

* Distributed indexing and searching and transparent failover
* Full JSON api
* Centralized index management
* Near-realtime search

Usage
-------
Solr uses Zookeeper for distributed capabilities, so we will take advantage of that to:

* detect live nodes, 
* remove failing nodes
* find cluster health


     >>> zk = ZConnection("localhost:9983")
     >>> solr = SolrRequest(zk,"collection1")
     >>> print solr.search(q="*:*")
     ...

 