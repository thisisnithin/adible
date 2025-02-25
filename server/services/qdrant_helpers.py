import os
from typing import List, Any

from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.readers.file import CSVReader
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from dotenv import load_dotenv
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

load_dotenv("server/.env")

data = CSVReader(concat_rows=False)

from qdrant_client import QdrantClient

qdrant_client = QdrantClient(url="https://7c7d58d4-2651-42a3-9ee4-bcef1e1a0029.eu-central-1-0.aws.cloud.qdrant.io", api_key=os.getenv("QDRANT_API_KEY"))

embed_model = OpenAIEmbedding()

def index_data(rows:List[Any],collection_name:str = "adible"):
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # Vectorize and load data into Qdrant
    print("Indexing data...")
    docs = []
    for row in rows:
        doc_id = row[0]
        # if check_if_id_exists_in_qdrant(doc_id, collection_name):
        #     print(f"Document with id {doc_id} already exists, skipping.")
        #     continue
        # if len(row) != 5:
        #     print(f"Row {row} has an unexpected number of columns, skipping!!!")
        #     continue
        text = "Title: " + row[2] + "\n\t" + row[3]
        doc = Document(
            text = text,
            metadata={"id": doc_id, "url": row[1], "title": row[2], "tags": row[4].split(",")},
        )
        docs.append(doc)
    # Create index and add nodes
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context,embed_model=embed_model)
    print(index)
    print("Indexing complete.")


def check_if_id_exists_in_qdrant(doc_id: int, collection_name: str) -> bool:
    """
    Check if a document with a given 'id' exists in the specified Qdrant collection.
    """
    filter_condition = Filter(
        must=[FieldCondition(key="id", match=MatchValue(value=doc_id))]
    )
    # 'scroll' returns a tuple: (points: List, next_page_token)
    result = qdrant_client.scroll(
        collection_name=collection_name,
        scroll_filter=filter_condition,
        limit=1
    )
    points = result[0]
    return len(points) > 0

def get_by_id(doc_id:str, collection_name:str = "adible"):
    """
    Get a document by its ID from the Qdrant collection.
    """
    filter_condition = Filter(
        must=[FieldCondition(key="id", match=MatchValue(value=doc_id))]
    )
    # 'scroll' returns a tuple: (points: List, next_page_token)
    result = qdrant_client.scroll(
        collection_name=collection_name,
        scroll_filter=filter_condition,
        limit=1
    )
    points = result[0]
    if len(points) < 1:
        return "https://example.com"
    return points # points[0].payload["url"]

def similarity_search(query:str, collection_name:str = "adible") :
    """
    Perform a similarity search on the Qdrant collection.
    """
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=collection_name)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store,embed_model=embed_model)
    q_engine: BaseQueryEngine = index.as_query_engine()
    resp = q_engine.query(query)
    return resp