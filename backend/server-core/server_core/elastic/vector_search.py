import logging
import os
import time
from typing import List, Dict, Optional

from asset_utils.common.singleton import Singleton
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from server_core.configs.configs import ConfigModes
from server_core.utils.file_utils import FileUtils

logger = logging.getLogger(__file__)


class ElasticVectorSearch(Singleton):
    # using singleton to ensure loading the transformer model only once - since it can be heavy
    def post_init(self, host):
        if not host:
            raise ValueError("Invalid ElasticSearch configuration missing host, index_name or index_map")

        self.es = Elasticsearch(host)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
        self.health_check()  # Perform health check

    def health_check(self):
        try:
            health = self.es.cluster.health()
            cluster_status = health.get('status')
            logger.critical(f"Elasticsearch cluster health: {cluster_status}")
            if cluster_status in ['red', 'yellow']:
                logger.warning("Elasticsearch cluster is in RED or YELLOW state")
            else:
                logger.critical("Elasticsearch cluster is in GREEN state.")

        except Exception as e:
            logger.critical(f"Failed to initialize Elasticsearch: {e}")

    @staticmethod
    def elastic_host(mode):
        # assuming we are running elastic on the same VM
        # allowing for override here in case developers want to run elastic on a different host
        if mode == ConfigModes.DEV:
            return os.getenv("ELASTIC_HOST", "http://localhost:9200")
        elif mode == ConfigModes.USER_TEST:
            return os.getenv("ELASTIC_HOST", "http://localhost:9200")
        elif mode == ConfigModes.PRODUCTION:
            return os.getenv("ELASTIC_HOST", "http://localhost:9200")
        elif mode == ConfigModes.TEST:
            return os.getenv("ELASTIC_HOST", "http://localhost:9200")
        else:
            raise ValueError("Invalid mode for asset index")

    def create_index(self, index_name, index_map, exists_ok=True):
        """Create index with vector mapping and string-based metadata handling"""

        # Delete existing index if force is True
        index_exists = self.es.indices.exists(index=index_name)

        if index_exists and not exists_ok:
            self.es.indices.delete(index=index_name)
            index_exists = False

        if not index_exists:
            self.es.indices.create(index=index_name, body=index_map)
            print(f"Created index: {index_name}")
        else:
            print(f"Index already exists: {index_name}")

    def index_document(self, index_name, document: Dict):
        """Index a single document with vector embedding and prepared metadata"""
        try:
            # Index document
            if "id" not in document:
                raise ValueError("Document ID is required for upsert")

            result = self.es.index(index=index_name, document=document, id=document['id'])
            print(f"Indexed document: {document['title']}")
            return result

        except Exception as e:
            print(f"Error indexing document {document.get('title', 'unknown')}: {str(e)}")
            raise

    def update_document(self, index_name, document: Dict, upsert=False):
        """Update a single document with vector embedding and prepared metadata
        If upsert is True, the document will be created if it does not exist
        """
        try:
            if "id" not in document:
                raise ValueError("Document ID is required for upsert")
            result = self.es.update(index=index_name, id=document["id"], doc=document, doc_as_upsert=upsert)
            return result

        except Exception as e:
            print(f"Error upserting document {document.get('title', 'unknown')}: {str(e)}")
            raise

    def document_exists(self, index_name, doc_id: str) -> bool:
        """Verify if a document exists in the index"""
        try:
            return self.es.exists(
                index=index_name,
                id=doc_id,
                refresh=True  # Ensure we have the latest state
            )
        except Exception as e:
            print(f"Error verifying document {doc_id}: {str(e)}")
            return False

    def get_document(self, index_name, doc_id: str) -> Optional[Dict]:
        """Retrieve a document from the index"""
        try:
            return self.es.get(index=index_name, id=doc_id)
        except Exception as e:
            print(f"Error retrieving document {doc_id}: {str(e)}")
            return None

    def hybrid_search(self,
                      index_name: str,
                      query_vector: dict,
                      k: int = 5,
                      min_score: float = 0.1,
                      offset: int = 0) -> List[Dict]:

        """offset = 0 and k = 10-> Results 0-9"""

        response = self.es.search(
            index=index_name,
            body={
                "query": query_vector,
                "min_score": min_score,
                "highlight": {
                    "fields": {
                        "*": {}  # Highlight all fields
                    }
                }
            },
            size=k,
            from_=offset  # Add from_ parameter
        )
        return response


def run_test():
    """Run a test with various metadata values and timing measurements"""
    from server_core.elastic.asset_entry import AssetEntry

    search_engine = ElasticVectorSearch.shared(host="http://localhost:9200")

    # Create index
    print("\nCreating index...")
    start = time.time()
    AssetEntry.create_index(es=search_engine, exists_ok=False)
    print(f"Index creation took: {time.time() - start:.2f} seconds")

    start_total = time.time()
    # Load test data
    start = time.time()
    test_documents = FileUtils.read_json(os.path.join(os.path.dirname(__file__), "sample_data.json"))
    print(f"\nLoading test data took: {time.time() - start:.2f} seconds")

    try:
        # Index documents
        print("\nIndexing test documents...")
        start = time.time()
        for doc in test_documents:
            AssetEntry.index_document(es=search_engine, data=doc)

        indexing_time = time.time() - start
        print(f"Indexing {len(test_documents)} documents took: {indexing_time:.2f} seconds")

        # Wait for indexing
        time.sleep(5)
        print("Waiting 1 second for indexing to complete...")

        # Test document existence
        print("\nTesting document existence...")
        start = time.time()
        for doc in test_documents:  # Test first two documents
            doc_id = doc['id']
            exists = search_engine.document_exists(index_name=AssetEntry.index_name(), doc_id=doc_id)
            print(f"Document {doc_id} exists: {exists}")
            record = search_engine.es.get(index=AssetEntry.index_name(), id=doc_id)
            print("saved record: ", record)

        # Test non-existent document
        fake_id = "nonexistent_id"
        exists = search_engine.document_exists(index_name=AssetEntry.index_name(), doc_id=fake_id)
        print(f"Document {fake_id} exists: {exists}")
        exists_check_time = time.time() - start
        print(f"Document existence check took: {exists_check_time:.2f} seconds")

        # Basic search test
        print("\nTesting basic search...")
        start = time.time()
        qv = AssetEntry.query_vector(model=search_engine.model, query_text="drug")
        results = search_engine.hybrid_search(index_name=AssetEntry.index_name(), query_vector=qv)['hits']['hits']
        search_time = time.time() - start
        print(f"Basic search took: {search_time:.2f} seconds")
        print("Results:")
        for hit in results:
            print(f"Score: {hit['_score']:.4f}, Title: {hit['_source']['title']}")

        # Filtered search test
        print("\nTesting search with metadata filter...")
        filters = {
            "metadata.data_quality.completion_rate": "95"
        }
        start = time.time()
        qv = AssetEntry.query_vector(model=search_engine.model, query_text="drug", filters=filters)
        results = search_engine.hybrid_search(index_name=AssetEntry.index_name(), query_vector=qv)['hits']['hits']
        filtered_search_time = time.time() - start
        print(f"Filtered search took: {filtered_search_time:.2f} seconds")
        print("Results:")
        for hit in results:
            print(f"Score: {hit['_score']:.4f}, Title: {hit['_source']['title']}")

        # Print total execution time
        total_time = time.time() - start_total
        print(f"\nTotal execution time: {total_time:.2f} seconds")

        # Print performance summary
        print("\nPerformance Summary:")
        print("-" * 50)
        print(f"Data loading time:     {time.time() - start_total:.2f} seconds")
        print(f"Index creation time:   {indexing_time:.2f} seconds")
        print(f"Document indexing:     {indexing_time:.2f} seconds")
        print(f"Document exists check: {exists_check_time:.2f} seconds")
        print(f"Basic search time:     {search_time:.2f} seconds")
        print(f"Filtered search time:  {filtered_search_time:.2f} seconds")
        print(f"Total execution time:  {total_time:.2f} seconds")
        print("-" * 50)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def get_document():
    from server_core.elastic.asset_entry import AssetEntry
    search_engine = ElasticVectorSearch.shared(host="http://localhost:9200")
    test_data = FileUtils.read_json(os.path.join(os.path.dirname(__file__), "sample_data.json"))
    for doc in test_data:
        document = search_engine.get_document(index_name=AssetEntry.index_name(), doc_id=doc['id'])
        print(document)


if __name__ == "__main__":
    run_test()
    # get_document()
