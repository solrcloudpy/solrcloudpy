from __future__ import print_function
from solrcloudpy import SolrConnection
import os

connection = SolrConnection(['localhost:8983', 'localhost:7574'], version=os.getenv('SOLR_VERSION', '5.3.2'))
for collection_name in connection.list():
    print("Dropping %s" % collection_name)
    connection[collection_name].drop()
