import logging

from solrcloudpy.collection import SolrCollection
from solrcloudpy.connection import SolrConnection
from solrcloudpy.parameters import SearchOptions

logging.basicConfig()

__version__ = "3.0.4"
__all__ = ["SolrCollection", "SolrConnection", "SearchOptions"]
