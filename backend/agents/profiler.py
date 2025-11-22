"""
Agent B: The Profiler
Parses resume PDF, creates embeddings, and stores in vector database
"""

from typing import Dict, Any, List


class ProfilerAgent:
    """
    Responsible for student intelligence:
    - Parse PDF resume
    - Chunk text for embedding
    - Create and store embeddings in ChromaDB

    Output: Vector store ready for RAG queries
    """

    def __init__(self, vector_store):
        """
        Initialize Profiler Agent

        Args:
            vector_store: ChromaDB vector store instance
        """
        self.vector_store = vector_store
        # PDF parser is a stateless utility module, no init needed

    async def parse_resume_pdf(self, pdf_path: str) -> str:
        """
        Extract text from resume PDF

        Args:
            pdf_path: Path to resume PDF file

        Returns:
            Extracted text content
        """
        from utils.pdf_parser import parse_pdf, validate_pdf
        
        # Validate PDF first
        is_valid, error = validate_pdf(pdf_path)
        if not is_valid:
            raise ValueError(f"Invalid PDF: {error}")
            
        # Parse PDF
        return parse_pdf(pdf_path)

    def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Full resume text
            chunk_size: Maximum characters per chunk (default 1000 for better context)

        Returns:
            List of text chunks
        """
        if not text:
            return []
            
        # Simple overlapping chunking strategy
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            
            # If we're not at the end, try to find a sentence break
            if end < text_len:
                # Look for period, newline, or space to break on
                # Prioritize period > newline > space
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                
                if last_period != -1 and last_period > start + chunk_size * 0.5:
                    end = last_period + 1
                elif last_newline != -1 and last_newline > start + chunk_size * 0.5:
                    end = last_newline + 1
                else:
                    # Fallback to last space
                    last_space = text.rfind(' ', start, end)
                    if last_space != -1:
                        end = last_space + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Overlap by 10% for context continuity
            start = end - int(chunk_size * 0.1)
            
            # Ensure we move forward
            if start >= end:
                start = end
                
        return chunks

    async def create_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks
        
        Args:
            chunks: List of text chunks

        Returns:
            List of embedding vectors
        """
        # ChromaDB handles embedding generation automatically by default
        # We don't need to manually generate them unless we're using a custom model
        # This method is kept for interface compatibility if we switch to manual embeddings later
        return []

    async def store_in_vector_db(
        self, 
        chunks: List[str], 
        session_id: str,
        embeddings: List[List[float]] = None
    ) -> None:
        """
        Store chunks and embeddings in ChromaDB

        Args:
            chunks: Text chunks
            session_id: Unique session identifier for isolation
            embeddings: Corresponding embedding vectors (optional, ChromaDB handles this)
        """
        if not chunks:
            return
        
        print(f"📝 [ProfilerAgent] Storing resume for session: {session_id}")
            
        # Add to vector store with session_id for isolation
        self.vector_store.add_documents(
            documents=chunks,
            metadatas=[
                {
                    "source": "resume", 
                    "chunk_index": i,
                    "session_id": session_id  # Session isolation
                } 
                for i in range(len(chunks))
            ]
        )
        
        print(f"✓ [ProfilerAgent] Stored {len(chunks)} chunks for session: {session_id}")

    async def run(self, resume_pdf_path: str, session_id: str) -> Dict[str, Any]:
        """
        Execute Profiler Agent workflow

        Args:
            resume_pdf_path: Path to student's resume PDF
            session_id: Unique session identifier for isolation

        Returns:
            Dict containing:
                - success: Boolean indicating completion
                - chunks_stored: Number of chunks stored
                - resume_text: Full extracted text
                - session_id: Session identifier used
        """
        try:
            # 1. Parse PDF
            resume_text = await self.parse_resume_pdf(resume_pdf_path)
            
            # 2. Chunk text
            chunks = self.chunk_text(resume_text)
            
            if not chunks:
                return {
                    "success": False,
                    "error": "No text extracted from PDF",
                    "chunks_stored": 0
                }
            
            # 3. Store in vector DB (embeddings handled automatically)
            await self.store_in_vector_db(chunks, session_id)
            
            return {
                "success": True,
                "chunks_stored": len(chunks),
                "resume_text": resume_text,
                "session_id": session_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "chunks_stored": 0
            }
