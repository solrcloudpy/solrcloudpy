Searching a collection
=======================

Although one can use plain dictionaries to pass parameters to solr,
one can use the :class:`~solrcloudpy.parameters.SearchOptions` class
makes this task more convenient. Using this class, one can make the
following queries:

     - MLT search via the `commonparams` member variable
     - normal search via `mltparams` member variable
     - faceted search via the `facetparams` member variable

