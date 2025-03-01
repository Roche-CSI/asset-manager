from __future__ import annotations
import json
from typing import List, Dict, Any, Optional
from server_core.asset_client import versioning
from datetime import datetime
from server_core.configs.configs import Configs, ConfigModes
from server_core.elastic.elastic_mixin import ElasticMixin
from server_core.elastic.stringify_dict import StringifyDict


class AssetEntry(ElasticMixin):

    def __init__(self):
        self.id: str = None
        self.title: str = None
        self.description: str = None
        self.tags: List[str] = []  # Initialize as an empty list
        self.metadata: Dict[str, Any] = {}  # Initialize as an empty dictionary
        self.class_name: str = None
        self.class_id: str = None
        self.class_title: str = None
        self.class_type: str = None
        self.project_name: str = None
        self.project_id: str = None
        self.project_title: str = None
        self.root_version: Dict[str, Any] = {}
        self.leaf_version: Dict[str, Any] = {}
        self.owner: str = None
        self.created_by: str = None
        self.created_at: float = None
        self.modified_by: str = None
        self.modified_at: float = None
        self.alias: str = None
        self.seq_id: int = None
        self.name: str = None
        self.num_versions: int = None
        self.status: int = None
        self.class_status: int = None
        self.project_status: int = None
        self.es_score = None
        self.es_highlight = None

    @classmethod
    def create(cls, asset,
               class_name: str,
               class_id: str,
               class_title: str,
               class_status: int,
               class_type: str,
               project_name: str,
               project_id: str,
               project_title: str,
               project_status: int,
               es_score: float,
               es_highlight: Dict):

        root_version = asset.root_version()
        leaf_version = asset.leaf_version()

        instance = AssetEntry()
        instance.id: str = str(asset.id)
        instance.title: str = asset.title
        instance.description: str = asset.description
        instance.tags: List[str] = asset.tags
        instance.metadata: Dict[str, Any] = asset.metadata  # could be any level of nesting and contain any type of data
        instance.tags: List[str] = asset.tags
        instance.class_name: str = class_name
        instance.class_title: str = class_title
        instance.class_id: str = class_id
        instance.class_type: str = class_type
        instance.project_name: str = project_name
        instance.project_id: str = project_id
        instance.project_title = project_title
        instance.root_version: Dict[str, Any] = instance._parse_version(root_version)
        instance.leaf_version: Dict[str, Any] = instance._parse_version(leaf_version)
        instance.owner: str = asset.owner
        instance.created_by: str = asset.created_by
        instance.created_at: float = asset.created_at.timestamp()
        instance.modified_by: str = asset.modified_by
        instance.modified_at: float = asset.modified_at.timestamp() if asset.modified_at else None  # Changed to float to match created_at
        instance.alias: str = asset.alias
        instance.seq_id: int = asset.seq_id
        instance.name: str = f"{class_name}/{instance.seq_id}"
        if asset.leaf_version and hasattr(asset.leaf_version, "number"):
            instance.num_versions: int = versioning.version_to_int(asset.leaf_version.number)

        instance.status: int = asset.status
        instance.class_status = class_status
        instance.project_status = project_status
        instance.es_score = es_score
        instance.es_highlight = es_highlight
        return instance

    @classmethod
    def list_response(cls, response):
        if response.get("hits") and response.get("hits").get("hits"):
            asset_entries = [cls._cast_to_asset_entry(hit) for hit in response['hits']['hits']]
            total_records = response['hits']['total']['value']
            print(f"Global string search executed successfully. Total hits: {total_records}")

            return asset_entries, total_records

        return [], 0

    @classmethod
    def get_response(cls, response):
        _original_state = response['_source']
        return cls._cast_to_asset_entry(response)

    @staticmethod
    def convert_to_timestamp(timestamp: float) -> datetime:
        """
        Parse a date string to a timestamp.

        Args:
            date_string (str): The date string in ISO format.

        Returns:
            float: The timestamp.
        """
        return datetime.fromtimestamp(timestamp).timestamp()

    def _parse_version(self, version) -> Dict[str, Any]:
        return {
            "id": version.id,
            "created_at": version.created_at.timestamp(),
            "size": version.size,
            "num_objects": version.num_objects
        }

    @classmethod
    def _cast_to_asset_entry(cls, hit: Dict[str, Any]) -> AssetEntry:
        """
        Cast an Elasticsearch hit to an AssetEntry object.

        Args:
            hit (Dict[str, Any]): The Elasticsearch hit dictionary.

        Returns:
            AssetEntry: An AssetEntry object created from the hit data.
        """
        source = hit['_source']
        es_score = hit.get("_score", None)
        es_highlight = hit.get("highlight", None)

        entry = AssetEntry()
        for key, value in source.items():
            setattr(entry, key, value)

        entry.es_score = es_score
        entry.es_highlight = es_highlight

        if entry.created_at:
            entry.created_at = cls.convert_to_timestamp(entry.created_at)

        if entry.modified_at:
            entry.modified_at = cls.convert_to_timestamp(entry.modified_at)

        if entry.root_version and entry.root_version.get("created_at"):
            entry.root_version["created_at"] = cls.convert_to_timestamp(entry.root_version["created_at"])

        if entry.leaf_version and entry.leaf_version.get("created_at"):
            entry.leaf_version["created_at"] = cls.convert_to_timestamp(entry.leaf_version["created_at"])

        return entry

    @staticmethod
    def index_name():
        cfg = Configs.shared()
        if cfg.MODE == "DEV":
            return "asset_index_dev"
        elif cfg.MODE == "USER_TEST":
            return "asset_index_user_test"
        elif cfg.MODE == "PRODUCTION":
            return "asset_index_prod"
        elif cfg.MODE == "TEST":
            return "asset_index_unit_test"
        else:
            raise ValueError("Invalid mode for asset index")

    @staticmethod
    def index_map() -> Dict[str, Any]:

        """bug encounterd for tags and fixes "basecalling" tag was not searchable
        The standard tokenizer first splits "basecalling" into a single token
        The ngram_filter then creates n-grams of length 2-8 [min_gram, max_gram]
        When searching, you're using the standard analyzer which doesn't create n-grams
        The term "basecalling" (10 characters) is longer than max_gram (8)
        """

        return {
            "settings": {
                "index": {
                    "max_ngram_diff": 7,
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                },
                "analysis": {
                    "analyzer": {
                        "ngram_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "ngram_filter"]
                        },
                        "edge_ngram_analyzer": {
                            "type": "custom",
                            "tokenizer": "edge_ngram_tokenizer",
                            "filter": ["lowercase"]
                        }
                    },
                    "tokenizer": {
                        "edge_ngram_tokenizer": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 12,  # was 8 earlier, see the bug description above
                            "token_chars": ["letter", "digit"]
                        }
                    },
                    "filter": {
                        "ngram_filter": {
                            "type": "ngram",
                            "min_gram": 2,
                            "max_gram": 8
                        }
                    }
                }
            },
            "mappings": {
                "dynamic": True,
                "dynamic_templates": [
                    {
                        "metadata_strings": {
                            "path_match": "metadata.*",
                            "match_mapping_type": "string",
                            "mapping": {
                                "type": "keyword",
                                "fields": {
                                    "text": {
                                        "type": "text",
                                        "analyzer": "standard"
                                    },
                                    "ngram": {
                                        "type": "text",
                                        "analyzer": "ngram_analyzer",
                                        "search_analyzer": "standard"
                                    }
                                }
                            }
                        }
                    }
                ],
                "properties": {
                    "title": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "ngram": {
                                "type": "text",
                                "analyzer": "ngram_analyzer",
                                "search_analyzer": "standard"
                            },
                            "edge_ngram": {
                                "type": "text",
                                "analyzer": "edge_ngram_analyzer",
                                "search_analyzer": "standard"
                            }
                        }
                    },
                    "description": {
                        "type": "text",
                        "fields": {
                            "ngram": {
                                "type": "text",
                                "analyzer": "ngram_analyzer",
                                "search_analyzer": "standard"
                            },
                            "edge_ngram": {
                                "type": "text",
                                "analyzer": "edge_ngram_analyzer",
                                "search_analyzer": "standard"
                            }
                        }
                    },
                    "tags": {
                        "type": "text",
                        "fields": {
                            "ngram": {
                                "type": "text",
                                "analyzer": "ngram_analyzer",
                                "search_analyzer": "standard"
                            },
                            "exact": {
                                "type": "keyword"
                            }
                        }
                    },
                    "metadata": {
                        "type": "object",
                        "dynamic": True
                    },
                    "vector_embedding": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    },
                    "created_by": {
                        "type": "keyword",
                        "fields": {
                            "ngram": {
                                "type": "text",
                                "analyzer": "ngram_analyzer",
                                "search_analyzer": "standard"
                            },
                            "edge_ngram": {
                                "type": "text",
                                "analyzer": "edge_ngram_analyzer",
                                "search_analyzer": "standard"
                            }
                        }
                    },
                    "alias": {
                        "type": "keyword",
                        "fields": {
                            "ngram": {
                                "type": "text",
                                "analyzer": "ngram_analyzer",
                                "search_analyzer": "standard"
                            },
                            "edge_ngram": {
                                "type": "text",
                                "analyzer": "edge_ngram_analyzer",
                                "search_analyzer": "standard"
                            }
                        }
                    },
                    "class_type": {
                        "type": "keyword"  # Using keyword type for exact matching in filters
                    },
                    "project_id": {
                        "type": "keyword"  # Changed from object to keyword for filtering
                    },
                    "class_id": {
                        "type": "keyword"  # Changed from object to keyword for filtering
                    },

                    # Non-searchable fields marked as enabled:false, added to elastic for data completeness
                    "class_name": {"type": "object", "enabled": False},
                    "class_title": {"type": "object", "enabled": False},
                    "project_name": {"type": "object", "enabled": False},
                    "project_title": {"type": "object", "enabled": False},
                    "root_version": {"type": "object", "enabled": False},
                    "leaf_version": {"type": "object", "enabled": False},
                    "owner": {"type": "object", "enabled": False},
                    "modified_by": {"type": "object", "enabled": False},
                    "modified_at": {"type": "object", "enabled": False},
                    "created_at": {"type": "object", "enabled": False},
                    "seq_id": {"type": "object", "enabled": False},
                    "name": {"type": "object", "enabled": False},
                    "num_versions": {"type": "object", "enabled": False},
                    "status": {"type": "object", "enabled": False},
                    "class_status": {"type": "object", "enabled": False},
                    "project_status": {"type": "object", "enabled": False}
                }
            }
        }

    @staticmethod
    def prepare_for_indexing(model, document: dict):
        """prepare a document for indexing in Elasticsearch"""
        # Create a deep copy to avoid modifying the original
        doc_to_index = json.loads(json.dumps(document))

        # Ensure metadata exists and is properly formatted
        if 'metadata' not in doc_to_index:
            doc_to_index['metadata'] = {}

        # Prepare metadata
        metadata = StringifyDict(doc_to_index.get('metadata', {}) or {})
        doc_to_index['metadata'] = metadata.prepare()

        # Create embedding from title, description and tags
        text_to_embed = f"{doc_to_index['title']} {doc_to_index['description']} {' '.join(doc_to_index.get('tags', []))}"
        vector = model.encode(text_to_embed)

        # Add embedding to document
        doc_to_index['vector_embedding'] = vector.tolist()

        # Add timestamps if not present
        current_time = datetime.now().isoformat()
        doc_to_index.setdefault('created_at', current_time)
        doc_to_index.setdefault('modified_at', current_time)

        # Convert to JSON string and back to ensure proper serialization
        doc_json = json.dumps(doc_to_index)
        doc_to_index = json.loads(doc_json)

        return doc_to_index

    def prepare_for_update(self, model, document: dict):
        # if any of the embedding keys have changed, re-encode the embedding
        if any(key in document for key in ['title', 'description', 'tags']):
            text_to_embed = f"{document.get('title', self.title)} {document.get('description', self.description)} {' '.join(document.get('tags', self.tags))}"
            document['vector_embedding'] = model.encode(text_to_embed).tolist()

        # Prepare metadata
        if 'metadata' in document:
            metadata = StringifyDict(document.get('metadata') or {})
            document['metadata'] = metadata.prepare()

        current_time = datetime.now().isoformat()
        document.setdefault('modified_at', current_time)

        return document


    @staticmethod
    def query_vector(model,
                     query_text: str,
                     filters: Optional[Dict] = None,
                     vector_weight: float = 0.7) -> dict:
        """Enhanced hybrid search with metadata filtering support"""
        query_vector = model.encode(query_text)

        query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query_text,
                            "fields": [
                                "title.ngram^3",
                                "description.ngram^2",
                                "tags.ngram",
                                "metadata.*.text",
                                "created_by.ngram",
                                "alias.ngram",
                            ],
                            "type": "best_fields",
                            "fuzziness": "AUTO",
                            "prefix_length": 2,
                            "minimum_should_match": "75%"
                        }
                    }
                ],
                "should": [
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": f"cosineSimilarity(params.query_vector, 'vector_embedding') + 1.0",
                                "params": {"query_vector": query_vector.tolist()}
                            },
                            "boost": vector_weight
                        }
                    }
                ]
            }
        }

        if filters:
            filter_clauses = []
            for field, value in filters.items():
                if isinstance(value, (list, tuple)):
                    filter_clauses.append({"terms": {field: [str(v) for v in value]}})
                else:
                    filter_clauses.append({"term": {field: str(value)}})
            query["bool"]["filter"] = filter_clauses

        return query

    def to_json_dict(self, fields=None):
        data = super().to_dict(fields)
        if "created_at" in data:
            data["created_at"] = datetime.fromtimestamp(data["created_at"]).isoformat()
        if "modified_at" in data:
            data["modified_at"] = datetime.fromtimestamp(data["modified_at"]).isoformat()

    @staticmethod
    def frontend_fields():
        return AssetEntry.elastic_fields() + ["es_score", "es_highlight"]

    @staticmethod
    def elastic_fields():
        return [
            "id",
            "title",
            "description",
            "tags",
            "metadata",
            "class_name",
            "class_id",
            "class_title",
            "class_type",
            "project_name",
            "project_id",
            "project_title",
            "root_version",
            "leaf_version",
            "owner",
            "created_by",
            "created_at",
            "modified_by",
            "modified_at",
            "alias",
            "seq_id",
            "name",
            "num_versions",
            "status",
            "class_status",
            "project_status",
        ]
