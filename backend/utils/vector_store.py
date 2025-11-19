"""
ChromaDB vector store wrapper for resume RAG
"""

import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings


class VectorStore:
    """
    Wrapper for ChromaDB vector store operations
    Handles resume embedding storage and retrieval
    """

    def __init__(self, collection_name: str = "resumes", persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB vector store

        Args:
            collection_name: Name for the ChromaDB collection
            persist_directory: Directory to persist vector store
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)

        # Ensure persist directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Resume chunks for RAG comparison"}
        )

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector store

        Args:
            documents: List of text chunks to store
            metadatas: Optional metadata for each document
            ids: Optional custom IDs for documents

        Raises:
            ValueError: If documents is empty or lengths don't match
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        # Create default metadata if not provided
        if metadatas is None:
            metadatas = [{"source": "resume"} for _ in documents]

        # Validate lengths match
        if len(documents) != len(ids) or len(documents) != len(metadatas):
            raise ValueError(
                f"Length mismatch: documents={len(documents)}, "
                f"ids={len(ids)}, metadatas={len(metadatas)}"
            )

        # Add to ChromaDB collection (ChromaDB handles embeddings automatically)
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(
        self,
        query_text: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar documents

        Args:
            query_text: Text to search for
            n_results: Number of results to return

        Returns:
            Dict containing:
                - documents: List of matching text chunks
                - distances: Similarity scores
                - metadatas: Associated metadata
                - ids: Document IDs
        """
        if not query_text or not query_text.strip():
            return {
                "documents": [],
                "distances": [],
                "metadatas": [],
                "ids": []
            }

        # Query ChromaDB collection (handles embedding automatically)
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        # Flatten results (ChromaDB returns list of lists)
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "ids": results["ids"][0] if results["ids"] else []
        }

    def query_with_filter(
        self,
        query_text: str,
        filter_dict: Dict[str, Any],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Query with metadata filtering

        Args:
            query_text: Text to search for
            filter_dict: Metadata filters to apply
            n_results: Number of results to return

        Returns:
            Filtered query results

        Example:
            >>> store.query_with_filter(
            ...     "python experience",
            ...     {"section": "experience"},
            ...     n_results=3
            ... )
        """
        if not query_text or not query_text.strip():
            return {
                "documents": [],
                "distances": [],
                "metadatas": [],
                "ids": []
            }

        # Query with metadata filter
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=filter_dict
        )

        # Flatten results
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "ids": results["ids"][0] if results["ids"] else []
        }

    def delete_collection(self) -> None:
        """
        Delete the entire collection
        Useful for cleanup or reset
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            # Recreate collection for continued use
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Resume chunks for RAG comparison"}
            )
        except Exception as e:
            print(f"Warning: Could not delete collection: {e}")

    def clear_collection(self) -> None:
        """
        Clear all documents from collection but keep collection
        """
        # Get all document IDs
        all_docs = self.collection.get()

        if all_docs["ids"]:
            # Delete all documents
            self.collection.delete(ids=all_docs["ids"])

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection

        Returns:
            Dict containing:
                - count: Number of documents
                - collection_name: Name of collection
                - persist_directory: Storage location
        """
        count = self.collection.count()

        return {
            "count": count,
            "collection_name": self.collection_name,
            "persist_directory": str(self.persist_directory)
        }

    def get_all_documents(self) -> Dict[str, Any]:
        """
        Retrieve all documents from the collection

        Returns:
            Dict containing all documents with their metadata and IDs
        """
        return self.collection.get()

    def update_document(
        self,
        document_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update an existing document

        Args:
            document_id: ID of document to update
            document: New document text (optional)
            metadata: New metadata (optional)

        Raises:
            ValueError: If neither document nor metadata provided
        """
        if document is None and metadata is None:
            raise ValueError("Must provide either document or metadata to update")

        update_args = {"ids": [document_id]}

        if document is not None:
            update_args["documents"] = [document]

        if metadata is not None:
            update_args["metadatas"] = [metadata]

        self.collection.update(**update_args)

    def delete_documents(self, document_ids: List[str]) -> None:
        """
        Delete specific documents by ID

        Args:
            document_ids: List of document IDs to delete
        """
        if document_ids:
            self.collection.delete(ids=document_ids)
