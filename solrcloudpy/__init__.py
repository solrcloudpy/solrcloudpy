from solrcloudpy.connection import SolrConnection
from solrcloudpy.collection import SolrCollection
from solrcloudpy.parameters import SearchOptions
import logging
logging.basicConfig()

__version__ = "1.7.460"
__all__ = ['SolrCollection', 'SolrConnection', 'SearchOptions']
