import os

from solrcloudpy import SolrConnection

connection = SolrConnection(
    ["localhost:8983", "localhost:7574"], version=os.getenv("SOLR_VERSION", "7.7.0")
)
for collection_name in connection.list():
    print("Dropping %s" % collection_name)
    connection[collection_name].drop()
