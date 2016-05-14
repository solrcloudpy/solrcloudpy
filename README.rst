solrcloudpy
===========

solrcloudpy is a python library for interacting with SolrCloud. This
library aims to take advantage of the following features of Solr:

* Distributed indexing and searching and transparent failover
* Full JSON api
* Centralized index management
* Near-realtime search

It is compatible with versions 4.6 up to 6.0.
The API is meant to be close to pymongo's API, where one can access
collections and databases as simple attributes 
or dictionary keys.

As of 2016, this library is maintained by the Solrcloudpy community.
Contributions are welcome.


Usage
-------
.. code-block:: python

     conn = SolrConnection(["localhost:9983","localhost:8984"], version="6.0.0")
     conn.create('test1',num_shards=1,replication_factor=2)

   
Access an existing collection:

.. code-block:: python

     conn.test_collection.search({'q':'query1'})
     conn["test_collection"].search({'q':'query2'})
     
Index documents:

.. code-block:: python

     docs = [{"id":"1", "name":"a"},{"id":"2","name":"b"}]
     collection.add(docs)

Search documents:

 .. code-block:: python

      collection.search({'q':'*:*'})
 
Console
-------
``solrcloudpy`` comes with a console that can be run simply by typing ``solrconsole``. More information on usage is available at
http://solrcloudpy.github.io/solrcloudpy/console.html

Documentation and API
---------------------
Documentation can be found at http://solrcloudpy.github.io/solrcloudpy/
