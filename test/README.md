Solrcloud tests
----------------

These are integration tests. Each test runs against a live solr
server, taken from the stock solr distribution.

Running the tests
------------------
First, modify where the solr jar can be found in
`solr_instance.py`. Then run a test, ie `python test_collection`.
