"""
Get and modify schema
"""
from solrcloudpy.utils import _Request


class SolrSchema(object):
    """
    Get and modify schema.
    Uses the Schema API described in https://cwiki.apache.org/confluence/display/solr/Schema+API
    """
    def __init__(self, connection, collection_name):
        """
        :param connection: the connection to solr
        :type connection: SolrConnection
        :param collection_name: the name of the collection related to the schema
        :type collection_name: str
        """
        self.connection = connection
        self.collection_name = collection_name
        self.client = _Request(connection)

    @property
    def schema(self):
        """
        Retrieves the schema as a dict
        :return: the schema dict
        :rtype: dict
        """
        return self.client.get('%s/schema' % self.collection_name).result.dict

    @property
    def name(self):
        """
        Retrieves the schema name as a dict
        :return: the schema name as a dict
        :rtype: dict
        """
        return self.client.get('%s/schema/name' % self.collection_name).result.dict

    @property
    def version(self):
        """
        Retrieves the schema version as a dict
        :return: the schema version as a dict
        :rtype: dict
        """
        return self.client.get('%s/schema/version' % self.collection_name).result.dict

    @property
    def unique_key(self):
        """
        Retrieves the schema's defined unique key as a dict
        :return: the schema unique key as a dict
        :rtype: dict
        """
        return self.client.get('%s/schema/uniquekey' % self.collection_name).result.dict

    @property
    def similarity(self):
        """
        Retrieves the schema's global similarity definition as a dict
        :return: the schema global similarity definition as a dict
        :rtype: dict
        """
        return self.client.get('%s/schema/similarity' % self.collection_name).result.dict

    @property
    def default_operator(self):
        """
        Retrieves the schema's defualt operator as a dict
        :return: the schema default operator as a dict
        :rtype: dict
        """
        return self.client.get('%s/schema/solrqueryparser/defaultoperator' % self.collection_name).result.dict

    def get_field(self, field):
        """
        Get information about a field in the schema
        TODO: looks like this API will change in newer versions of solr

        :param field: the name of the field
        :type field: str
        :return: a dict related to the field definition
        :rtype: dict
        """
        return self.client.get('%s/schema/field/%s' % (self.collection_name, field)).result.dict

    def get_fields(self):
        """
        Get information about all field in the schema
        
        :return: a dict of fields to their schema definitions
        :rtype: dict
        """
        return self.client.get('%s/schema/fields' % self.collection_name).result.dict

    def add_fields(self, json_schema):
        """
        Add fields to the schema

        :param json_schema: specs for the fields to add -- should be a json string
        :type json_schema: str
        :return: a dict representing the result of the update request
        :rtype: dict
        """
        return self.client.update('%s/schema/fields' % self.collection_name, body=json_schema).result.dict

    def get_dynamic_fields(self):
        """
        Get information about a dynamic field in the schema
        :return: a dict of dynamic fields to their schema definitions
        :rtype: dict
        """
        return self.client.get('%s/schema/dynamicfields' % self.collection_name).result.dict

    def get_dynamic_field(self, field):
        """
        Get information about a dynamic field in the schema
        TODO: this will change in later version of solr

        :param field: the name of the field
        :type field: str
        :return: a dict of dynamic fields to their schema definitions
        :rtype: dict
        """
        return self.client.get('%s/schema/dynamicfield/%s' % (self.collection_name, field)).result.dict

    def get_fieldtypes(self):
        """
        Get information about field types in the schema
        :return: a dict relating information about field types
        :rtype: dict
        """
        return self.client.get('%s/schema/fieldtypes' % (self.collection_name)).result.dict

    def get_fieldtype(self, ftype):
        """
        Get information about a field type in the schema

        :param ftype: the name of the field type
        :type ftype: str
        :return: a dict relating information about a given field type
        :rtype: dict
        """
        return self.client.get('%s/schema/fieldtypes/%s' % (self.collection_name, ftype)).result.dict

    def get_copyfields(self):
        """
        Get information about all copy field in the schema
        :return: a dict describing the copyfields defined in the schema
        :rtype: dict
        """
        return self.client.get('%s/schema/copyfields' % self.collection_name).result.dict

    def get_copyfield(self, field):
        """
        Get information about a copy field in the schema

        :param ftype: the name of the field type
        :type ftype: str
        :return: a dict relating information about a given copyfield
        :rtype: dict
        """
        return self.client.get('%s/schema/copyfield/%s' % (self.collection_name, field)).result.dict
