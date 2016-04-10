from solrcloudpy import SolrConnection

connection = SolrConnection(['localhost:8983', 'localhost:7574'])
for collection_name in connection.list():
    print "Dropping %s" % collection_name
    connection[collection_name].drop()
