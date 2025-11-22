"""
Anthropic API client wrapper for standardized LLM calls
"""

from typing import Optional
from anthropic import AsyncAnthropic


class LLMClient:
    """
    Simple wrapper for Anthropic API calls
    Initialize once per agent with desired settings, then call repeatedly
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        Initialize Anthropic API client

        Args:
            api_key: Anthropic API key
            model: Model identifier (default: Claude 3.5 Sonnet)
            temperature: Sampling temperature (0.0-1.0, lower for structured output)
            max_tokens: Maximum tokens in response
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def call(
        self,
        system_prompt: str,
        user_message: str
    ) -> str:
        """
        Call Anthropic API and return text response

        Args:
            system_prompt: System instruction for the model
            user_message: User input/query

        Returns:
            Generated text response (agents handle JSON parsing if needed)

        Raises:
            ValueError: If API call fails

        Example:
            >>> client = LLMClient(api_key="...", temperature=0.3)
            >>> response = await client.call(
            ...     system_prompt="You are a scholarship analyst. Return only JSON.",
            ...     user_message="Analyze this scholarship..."
            ... )
            >>> result = json.loads(response)  # Agent parses JSON
        """
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            raise ValueError(f"Anthropic API call failed: {str(e)}")


def create_llm_client(
    api_key: Optional[str] = None,
    model: str = "claude-3-haiku-20240307",
    temperature: float = 0.7
) -> LLMClient:
    """
    Factory function to create LLM client with config defaults

    Args:
        api_key: Anthropic API key (if None, reads from settings)
        model: Model identifier
        temperature: Sampling temperature

    Returns:
        Configured LLMClient instance

    Example:
        >>> from config.settings import settings
        >>> client = create_llm_client(api_key=settings.anthropic_api_key)
    """
    if api_key is None:
        from config.settings import settings
        api_key = settings.anthropic_api_key

    if not api_key:
        raise ValueError(
            "Anthropic API key not provided and not found in settings. "
            "Set ANTHROPIC_API_KEY environment variable."
        )

    return LLMClient(
        api_key=api_key,
        model=model,
        temperature=temperature
    )
