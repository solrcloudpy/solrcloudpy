"""
Get and modify schema
"""
from solrcloudpy.utils import _Request

class SolrSchema(object):
    """
    Get and modify schema
    """
    def __init__(self,connection,collection_name):
        self.connection = connection
        self.collection_name = collection_name
        self.client = _Request(connection)

    @property
    def schema(self):
        path = '%s/schema'% (self.collection_name)
        return self.client.get(path,{}).result.dict

    @property
    def name(self):
        path = '%s/schema/name'% (self.collection_name)
        return self.client.get(path,{}).result.dict

    @property
    def version(self):
        path = '%s/schema/version'% (self.collection_name)
        return self.client.get(path,{}).result.dict

    @property
    def unique_key(self):
        path = '%s/schema/uniquekey'% (self.collection_name)
        return self.client.get(path,{}).result.dict

    @property
    def similarity(self):
        path = '%s/schema/similarity'% (self.collection_name)
        return self.client.get(path,{}).result.dict

    @property
    def default_operator(self):
        path = '%s/schema/solrqueryparser/defaultoperator'% (self.collection_name)
        return self.client.get(path,{}).result.dict

    ## fields
    def get_field(self,field):
        """
        Get information about a field in the schema

        :param field: the name of the field
        """
        path = '%s/schema/field/%s'% (self.collection_name,field)
        return self.client.get(path,{}).result.dict

    def get_fields(self):
        """
        Get information about all field in the schema
        """
        path = '%s/schema/fields'%self.collection_name
        return self.client.get(path,{}).result.dict

    def add_fields(self,json_schema):
        """
        Add fields to the schema

        :param json_schema: specs for the fields to add
        """
        path = '%s/schema/fields'%self.collection_name
        return self.client.update(path,{},json_schema).result.dict

    ## dynamic fields
    def get_dynamic_fields(self):
        """
        Get information about a dynamic field in the schema
        """
        path = '%s/schema/dynamicfields'%self.collection_name
        return self.client.get(path,{}).result.dict

    def get_dynamic_field(self,field):
        """
        Get information about a dynamic field in the schema

        :param field: the name of the field
        """
        path = '%s/schema/dynamicfield/%s'%(self.collection_name,field)
        return self.client.get(path,{}).result.dict

    ## field types
    def get_fieldtypes(self):
        """
        Get information about field types in the schema
        """
        path = '%s/schema/fieldtypes'%(self.collection_name)
        return self.client.get(path,{}).result.dict

    def get_fieldtype(self,ftype):
        """
        Get information about a field type in the schema

        :param ftype: the name of the field type
        """
        path = '%s/schema/fieldtypes/%s'%(self.collection_name,ftype)
        return self.client.get(path,{}).result.dict

    ## copy fields
    def get_copyfields(self):
        """
        Get information about all copy field in the schema
        """
        path = '%s/schema/copyfields'%self.collection_name
        return self.client.get(path,{}).result.dict

    def get_copyfield(self,field):
        """
        Get information about a copy field in the schema

        :param ftype: the name of the field type
        """
        path = '%s/schema/copyfield/%s'%(self.collection_name,field)
        return self.client.get(path,{}).result.dict
