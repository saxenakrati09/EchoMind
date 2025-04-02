
import os
import hashlib
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RAGSystem:
    def __init__(self, docs_path: str, index_path: str = "faiss_index"):
        """
        Args:
            docs_path: Path to documents directory (relative to calling script)
            index_path: Path to save/load FAISS index
        """
        self.docs_path = Path(docs_path)
        self.index_path = Path(index_path)
        self.index = None
        self.embeddings = OpenAIEmbeddings()
        
        if not self.docs_path.exists():
            raise FileNotFoundError(f"Documents directory not found: {self.docs_path}")

    def _compute_chunk_hash(self, chunk):
        """Compute stable hash for document chunk"""
        content = chunk.page_content
        metadata = str(sorted(chunk.metadata.items()))
        return hashlib.sha256((content + metadata).encode()).hexdigest()

    def _get_existing_hashes(self):
        """Retrieve hashes from existing index"""
        if self.index and hasattr(self.index, "docstore"):
            return set(self.index.docstore._dict.keys())
        return set()

    def build_or_update_index(self):
        """Build/update FAISS index with documents"""
        # Load existing index if available
        if self.index_path.exists():
            print(f"Loading existing index from {self.index_path}")
            self.index = FAISS.load_local(
                self.index_path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            existing_hashes = self._get_existing_hashes()
        else:
            self.index = None
            existing_hashes = set()

        # Process documents
        loader = DirectoryLoader(
            str(self.docs_path), 
            glob="**/*.txt", 
            loader_cls=TextLoader
        )
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        chunks = splitter.split_documents(documents)

        # Find new chunks
        new_chunks, new_hashes = [], []
        for chunk in chunks:
            chunk_hash = self._compute_chunk_hash(chunk)
            if chunk_hash not in existing_hashes:
                new_chunks.append(chunk)
                new_hashes.append(chunk_hash)

        if not new_chunks:
            print("No new content to add")
            return self.index

        # Update index
        if self.index:
            print(f"Adding {len(new_chunks)} new chunks")
            self.index.add_documents(new_chunks, ids=new_hashes)
        else:
            print("Creating new index")
            self.index = FAISS.from_documents(
                new_chunks, 
                self.embeddings, 
                ids=new_hashes
            )

        # Save updated index
        self.index.save_local(str(self.index_path))
        print(f"Index saved to {self.index_path}")
        return self.index

    def retrieve_content(self, query: str, k: int = 5) -> str:
        """Search index for relevant content"""
        if not self.index:
            raise ValueError("Index not initialized. Call build_or_update_index() first")
            
        results = self.index.similarity_search(query, k=k)
        return "\n---\n".join(doc.page_content for doc in results) if results else ""