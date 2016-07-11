Solrcloud tests
----------------

These are integration tests. Each test runs against a live solr
server, taken from the stock solr distribution.

Running the tests
------------------
You can run these tests by setting SOLR_HOME in your enviornment 
as the path to where a solr executable jar lives. 
`solr_instance.py` uses that information to create a connection to solr. 
An example of in a test run would be 
`SOLR_HOME=/home/dfdeshom/code/solr-4.6.0/example/solr python test_collection`,
or you could export it.

Without the solr collection, we won't perform any of the buildup and tear-down, but 
will assume there is a Solr instance running at localhost:8983.

With recent versions of Solr, a configName argument is compulsory for creating
collections, in which case, also set `SOLR_CONFNAME=myconfig` in the
environment, assuming `myconfig` is already uploaded as a config to Solr.
