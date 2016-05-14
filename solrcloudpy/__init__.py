from solrcloudpy.connection import SolrConnection
from solrcloudpy.collection import SolrCollection
from solrcloudpy.parameters import SearchOptions
import logging
logging.basicConfig()

__version__ = "2.0.1"
__all__ = ['SolrCollection', 'SolrConnection', 'SearchOptions']
