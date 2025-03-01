import time
import json
from typing import Any, Dict, Optional, List
from datetime import datetime
from server_core.elastic.vector_search import ElasticVectorSearch
from server_core.elastic.deep_compare_dict import DeepCompareDict


class ElasticMixin:

    @staticmethod
    def index_map():
        raise NotImplementedError("index_map method must be implemented in subclass")

    @staticmethod
    def index_name():
        raise NotImplementedError("index_name method must be implemented in subclass")

    @staticmethod
    def prepare_for_indexing(model, document: dict):
        raise NotImplementedError("prepare_for_indexing method must be implemented in subclass")

    def prepare_for_update(self, model, document: dict):
        raise NotImplementedError("prepare_for_update method must be implemented in subclass")

    @classmethod
    def create_index(cls, es: ElasticVectorSearch, exists_ok=True):
        es.create_index(index_name=cls.index_name(), index_map=cls.index_map(), exists_ok=exists_ok)

    @classmethod
    def index_document(cls, es: ElasticVectorSearch, data):
        doc = cls.prepare_for_indexing(model=es.model, document=data)
        return es.index_document(index_name=cls.index_name(), document=doc)

    def update_document(self, es: ElasticVectorSearch, data):
        doc = self.prepare_for_update(model=es.model, document=data)
        return es.update_document(index_name=self.index_name(), document=doc)

    @staticmethod
    def elastic_fields():
        raise NotImplementedError("elastic_fields method must be implemented in subclass")

    def upsert(self, es: ElasticVectorSearch, user: str):
        return self.__class__.upsert_document(es=es, data=self.to_dict(fields=self.elastic_fields()), user=user)

    @classmethod
    def upsert_document(cls, es: ElasticVectorSearch, data: dict, user: str):
        """
        operation = response['result']  # Will be either 'created' or 'updated'
        status = 201 if operation == 'created' else 200

        Parameters
        ----------
        es
        data
        user

        Returns
        -------

        """
        doc_id = data.get('id')
        if not doc_id:
            raise ValueError("missing required field: id")

        # verify if the document exists
        entry: ElasticMixin = cls.get(es=es, doc_id=doc_id)
        if entry:
            # find the fields that have changed
            existing = DeepCompareDict(entry.to_dict(fields=entry.elastic_fields()))
            new = DeepCompareDict(data)
            # pop 'modified_at' and 'modified_by' fields to compare
            for key in ['modified_at', 'modified_by']:
                existing.pop(key, None)
                new.pop(key, None)
            updates = existing.get_updates(new)
            if not updates:
                return None

            # add back id, we need it for updates
            updates['id'] = doc_id
            # update the document
            updates['modified_at'] = time.time()
            updates['modified_by'] = user
            res = entry.update_document(es=es, data=updates)
            return res['result']
        # if not, create document
        res = cls.index_document(es=es, data=data)
        return res['result']

    @classmethod
    def document_exists(cls, es: ElasticVectorSearch, doc_id: str):
        return es.document_exists(index_name=cls.index_name(), doc_id=doc_id)

    @staticmethod
    def query_vector(model, query_text, filters=None):
        raise NotImplementedError("query_vector method must be implemented in subclass")

    @staticmethod
    def list_response(response):
        raise NotImplementedError("from_search_response method must be implemented in subclass")

    @staticmethod
    def get_response(response):
        raise NotImplementedError("from_search_response method must be implemented in subclass")

    @classmethod
    def search(cls,
               es: ElasticVectorSearch,
               query: str,
               filters: dict = None,
               size: int = 10,
               offset: int = 0):
        """Search the index using the provided query and filters"""
        qv = cls.query_vector(model=es.model, query_text=query, filters=filters)
        response = es.hybrid_search(
            index_name=cls.index_name(),
            query_vector=qv,
            k=size,
            offset=offset
        )
        return cls.list_response(response) if response else []

    @classmethod
    def get(cls, es: ElasticVectorSearch, doc_id: str):
        response = es.get_document(index_name=cls.index_name(), doc_id=doc_id)
        return cls.get_response(response) if response else None

    @staticmethod
    def _convert_value(value: Any) -> Any:
        """
        Convert values to Elasticsearch-compatible formats.

        Handles:
        - datetime objects to timestamps
        - nested dictionaries
        - lists of objects
        - custom objects with to_dict method
        """
        if value is None:
            return None

        # Handle datetime objects
        if isinstance(value, datetime):
            return int(value.timestamp())

        # Handle lists (including lists of objects)
        if isinstance(value, list):
            return [ElasticMixin._convert_value(item) for item in value]

        # Handle dictionaries
        if isinstance(value, dict):
            return {k: ElasticMixin._convert_value(v) for k, v in value.items()}

        # Handle objects that have their own to_dict method
        if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
            return ElasticMixin._convert_value(value.to_dict())

        return value

    def to_dict(self, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Convert object to dictionary with proper timestamp handling.

        Parameters
        ----------
        fields : Optional[List[str]]
            List of fields to include in the output. If None, includes all fields.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the object with converted values

        Examples
        --------
        >> obj = MyElasticClass(created_at=datetime.now(), modified_at=datetime.now())
        >> obj.to_dict()
        {'created_at': 1637747200, 'modified_at': 1637747200, ...}
        """
        # Get the base dictionary
        if fields:
            data = {field: getattr(self, field) for field in fields if hasattr(self, field)}
        else:
            data = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

        # Convert all values to Elasticsearch-compatible formats
        converted_data = {k: ElasticMixin._convert_value(v) for k, v in data.items()}

        return converted_data