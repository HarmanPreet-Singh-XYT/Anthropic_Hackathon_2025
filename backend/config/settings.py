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
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

        # Paths
        self.base_dir: Path = Path(__file__).parent.parent
        self.prompts_dir: Path = self.base_dir / "prompts"
        self.data_dir: Path = self.base_dir / "data"
        self.chroma_dir: Path = self.data_dir / "chroma_db"

        # Model Configuration
        self.llm_model: str = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.7"))

        # LLM Provider Configuration
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic")  # "anthropic" or "openai"

        # Vector Store Configuration
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
        self.chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
        self.max_retrieval_results: int = int(os.getenv("MAX_RETRIEVAL_RESULTS", "5"))

        # Matchmaker Configuration
        self.match_threshold: float = float(os.getenv("MATCH_THRESHOLD", "0.8"))

        # Essay Configuration
        self.default_word_limit: int = int(os.getenv("DEFAULT_WORD_LIMIT", "500"))

        # Database Configuration
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql://scholarfit:scholarfit@localhost:5432/scholarfit"
        )

        # File Upload Configuration
        self.max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))
        self.allowed_file_types: list = [".pdf"]

        # Server Configuration
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.debug: bool = os.getenv("DEBUG", "False").lower() == "true"

        # CORS Origins
        self.cors_origins: list = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:3001"
        ).split(",")

        # Stripe Configuration
        self.stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
        self.stripe_publishable_key: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        self.stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

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
        if not self.anthropic_api_key and self.llm_provider == "anthropic":
            errors.append("ANTHROPIC_API_KEY is required but not set (LLM_PROVIDER=anthropic)")
        
        if not self.openai_api_key and self.llm_provider == "openai":
            errors.append("OPENAI_API_KEY is required but not set (LLM_PROVIDER=openai)")
        
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

        # Validate database URL format
        if not self.database_url.startswith("postgresql://"):
            errors.append(f"DATABASE_URL must start with 'postgresql://', got {self.database_url[:20]}...")

        # Validate server configuration
        if self.port <= 0 or self.port > 65535:
            errors.append(f"PORT must be between 1 and 65535, got {self.port}")

        if self.max_upload_size_mb <= 0:
            errors.append(f"MAX_UPLOAD_SIZE_MB must be positive, got {self.max_upload_size_mb}")

        # Return validation result
        return (len(errors) == 0, errors)

    @property
    def is_configured(self) -> bool:
        """
        Check if minimum required configuration is present

        Returns:
            True if API keys are set, False otherwise
        """
        llm_key_valid = (
            (self.llm_provider == "anthropic" and self.anthropic_api_key) or
            (self.llm_provider == "openai" and self.openai_api_key)
        )
        return bool(llm_key_valid and self.tavily_api_key)

    def get_database_components(self) -> dict:
        """
        Parse database URL into components
        
        Returns:
            Dictionary with database connection components
        """
        # Basic parsing of postgresql://user:password@host:port/database
        try:
            if not self.database_url.startswith("postgresql://"):
                return {}
            
            # Remove protocol
            url = self.database_url.replace("postgresql://", "")
            
            # Split user:password from rest
            auth, rest = url.split("@", 1)
            user, password = auth.split(":", 1)
            
            # Split host:port from database
            host_port, database = rest.split("/", 1)
            
            # Handle optional port
            if ":" in host_port:
                host, port = host_port.split(":", 1)
                port = int(port)
            else:
                host = host_port
                port = 5432
            
            return {
                "user": user,
                "password": password,
                "host": host,
                "port": port,
                "database": database.split("?")[0]  # Remove query params if any
            }
        except Exception:
            return {}

    def __repr__(self) -> str:
        """String representation of settings (without sensitive data)"""
        return (
            f"Settings(\n"
            f"  LLM Provider: {self.llm_provider}\n"
            f"  LLM Model: {self.llm_model}\n"
            f"  Database: {self.get_database_components().get('database', 'N/A')}\n"
            f"  ChromaDB: {self.chroma_dir}\n"
            f"  Server: {self.host}:{self.port}\n"
            f"  Debug: {self.debug}\n"
            f")"
        )


# Global settings instance
settings = Settings()