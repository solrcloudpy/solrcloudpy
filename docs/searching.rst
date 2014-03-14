Searching a collection
=======================

Although one can use plain dictionaries to pass parameters to solr,
the :class:`~solrcloudpy.parameters.SearchOptions` class
makes this task more convenient. Using this class, one can make the
following queries:

     - normal search via `commonparams`  member variable
     - MLT search via the `mltparams` member variable
     - faceted search via the `facetparams` member variable


Normal search
---------------

Most common search parameters are supported and can be chained. Method
names correspond to the parameters one passes to Solr. For common
search parameters, they can be found here: https://cwiki.apache.org/confluence/display/solr/Common+Query+Parameters

Example:

::

   >>> se.commonparams.q("nsa")
   >>> se.commonparams.fl("author,link").sort("pub_date desc")
   >>> se
   {'commonparams': {'q': set(['nsa']), 'sort': set(['pub_date desc']), 'fl': set(['author,link'])}, 'facetparams': {},'mltparams': {}}


Faceted search
---------------

Faceted search also supports most parameters one can pass to Solr from
the documentation: http://wiki.apache.org/solr/SimpleFacetParameters .

Example:

::

     >>> se = SearchOptions()
     >>> se.commonparams.q("*:*").fl('title,author')       
     {'q': set(['*:*']), 'fl': set(['title,author'])}
     >>> se.facetparams.field("author")
     {'facet.field': set(['id'])}
     >>> conn.collection1.search(se)
     {   
    "facet_counts": "SolrResponse << {'facet_ranges': {}, 'facet_fields': {\n    \"author\": \"SolrResponse << {'William Saletan': 1325, 'Jun ...  >>",
    "response": "SolrResponse << {'start': 0, 'numFound': 74104, 'docs': [{u'title': u'The Case for Getting Drunk at Work', u'author' ...  >>"
     }

More Like This search
------------------------

More Like This (MLT) is a Solr feature that returns documents similar
to the result of a query. This is supported in `solrcloudpy` via the
:meth:`~solrcloudpy.index.SolrIndex.mlt` method.

Example

::

   >>> se.commonparams.q("nsa")
   >>> se.mltparams.count("5")
   >>> conn.slatecogtree.mlt(se)
   {   
    "response": "SolrResponse << {'start': 0, 'numFound': 0, 'docs': []} >>",
    "match": "SolrResponse << {'start': 0, 'numFound': 590, 'docs': [{u'title': u'Booz Allen Fires NSA Leaker', u'section': u'brie...  >>"
   }

Working with query responses
-----------------------------

All query results are wrapped around a
:class:`~solrcloudpy.utils.SolrResponse` object.This object takes the
JSON response for the Solr server and makes its keys accessible  by
normal key syntax or attribute access  syntax. 

Example:

::

   >>> res = conn.collection1.search(se)
   >>> res
   {   
    "facet_counts": "SolrResponse << {'facet_ranges': {}, 'facet_fields': {\n    \"author\": \"SolrResponse << {'William Saletan': 1325, 'Jun ...  >>",
    "response": "SolrResponse << {'start': 0, 'numFound': 74104, 'docs': [{u'title': u'The Case for Getting Drunk at Work', u'author' ...  >>"
   }
   >>> res.facet_counts
   {   
    "facet_ranges": "SolrResponse << {} >>",
    "facet_fields": "SolrResponse << {'author': {\n    \"William Saletan\": 1325, \n    \"June Thomas\": 612, \n   \"Mike  Steinberger\": 103, \n   ...  >>",
    "facet_dates": "SolrResponse << {} >>",
    "facet_queries": "SolrResponse << {} >>"
   }
   >>> res.facet_counts.facet_fields.author['Aisha Harris']
   472


