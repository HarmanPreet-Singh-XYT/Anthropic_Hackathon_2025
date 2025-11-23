"""
Configuration management using environment variables
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables
    """

    def __init__(self):
        """Initialize settings from environment"""
        # API Keys
        self.anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
        self.google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
        self.google_cse_id: str = os.getenv("GOOGLE_CSE_ID", "")

        # Paths
        self.base_dir: Path = Path(__file__).parent.parent
        self.prompts_dir: Path = self.base_dir / "prompts"
        self.data_dir: Path = self.base_dir / "data"
        self.chroma_dir: Path = self.data_dir / "chroma_db"

        # Model Configuration
        self.llm_model: str = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.7"))

        # Vector Store Configuration
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
        self.chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
        self.max_retrieval_results: int = int(os.getenv("MAX_RETRIEVAL_RESULTS", "5"))

        # Matchmaker Configuration
        self.match_threshold: float = float(os.getenv("MATCH_THRESHOLD", "0.8"))

        # Essay Configuration
        self.default_word_limit: int = int(os.getenv("DEFAULT_WORD_LIMIT", "500"))

        # Ensure directories exist
        self._create_directories()

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate that all required settings are present

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required API keys
        if not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY is required but not set")
        if not self.tavily_api_key:
            errors.append("TAVILY_API_KEY is required but not set")

        # Validate paths exist
        if not self.base_dir.exists():
            errors.append(f"Base directory does not exist: {self.base_dir}")

        # Validate numeric ranges
        if not 0.0 <= self.temperature <= 1.0:
            errors.append(f"TEMPERATURE must be between 0.0 and 1.0, got {self.temperature}")
        
        if self.chunk_size <= 0:
            errors.append(f"CHUNK_SIZE must be positive, got {self.chunk_size}")
        
        if self.chunk_overlap < 0:
            errors.append(f"CHUNK_OVERLAP must be non-negative, got {self.chunk_overlap}")
        
        if self.chunk_overlap >= self.chunk_size:
            errors.append(f"CHUNK_OVERLAP ({self.chunk_overlap}) must be less than CHUNK_SIZE ({self.chunk_size})")
        
        if self.max_retrieval_results <= 0:
            errors.append(f"MAX_RETRIEVAL_RESULTS must be positive, got {self.max_retrieval_results}")
        
        if not 0.0 <= self.match_threshold <= 1.0:
            errors.append(f"MATCH_THRESHOLD must be between 0.0 and 1.0, got {self.match_threshold}")
        
        if self.default_word_limit <= 0:
            errors.append(f"DEFAULT_WORD_LIMIT must be positive, got {self.default_word_limit}")

        # Return validation result
        return (len(errors) == 0, errors)

    @property
    def is_configured(self) -> bool:
        """
        Check if minimum required configuration is present

        Returns:
            True if API keys are set, False otherwise
        """
        return bool(self.anthropic_api_key and self.tavily_api_key)


# Global settings instance
settings = Settings()