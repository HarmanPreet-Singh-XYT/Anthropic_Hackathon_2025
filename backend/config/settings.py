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
        # TODO: Create data directories
        # TODO: Create chroma_db directory
        pass

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate that all required settings are present

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # TODO: Check required API keys
        # TODO: Validate paths exist
        # TODO: Validate numeric ranges
        # TODO: Return validation result

        pass

    @property
    def is_configured(self) -> bool:
        """
        Check if minimum required configuration is present

        Returns:
            True if API keys are set, False otherwise
        """
        # TODO: Check essential configuration
        pass


# Global settings instance
settings = Settings()
