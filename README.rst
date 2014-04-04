solrcloudpy
===========

``solrcloudpy`` is a python library for interacting with SolrCloud. This library aims to take advantage of the following features of Solr:

* Distributed indexing and searching and transparent failover
* Full JSON api
* Centralized index management
* Near-realtime search

The API is meant to be close to pymongo's API, where one can access collections as simple attributes 
or dictionary keys.  

Example Usage
--------------

create a collection
::
   
     
     >>> conn = SolrConnection(["localhost:9983","localhost:8984"])
     >>> conn.create('test1',num_shards=1,replication_factor=2)
  
Access an existing collection

::
   
     
     >>> conn.test_collection.search({'q':'query1'})
     >>> conn["test_collection"].search({'q':'query2'})


Index documents

::
     
     >>> docs = [{"id":"1", "name":"a"},{"id":"2","name":"b"}]
     >>> collection.add(docs)


Search documents

::

     >>> collection.search({'q':'*:*'})

     
 
     
Console
-------
``solrcloudpy`` comes with a console that can be run simply by typing ``solrconsole``

.. code-block::

     $ solrconsole --host=localhost --port=8983 
     SolrCloud Console
     Use the 'conn' object to access a collection

     Type 'collections' to see the list of available collections
     solr localhost:8983> resp = conn.collection1.search({'q':'*:*'})
     solr localhost:8983> resp
     <SolrResponse [200]>
     solr localhost:8983> resp.result
     {   
         "response": "SolrResult << {'start': 0, 'numFound': 0, 'docs': []} >>"
     }

     solr localhost:8983> resp.result.response
     {
         "start": 0, 
         "numFound": 0, 
         "docs": []
     }


Documentation and API
---------------------
Documentation can be found at http://dfdeshom.github.io/solrcloudpy/ 
