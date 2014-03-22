from .admin import CollectionAdmin
from .search import CollectionSearch

class Collection(CollectionAdmin,CollectionSearch):
    pass

__all__ = ['Collection']
