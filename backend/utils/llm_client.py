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
        user_message: str,
        tools: Optional[list] = None
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
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            }
            
            # Add tools if provided
            if tools:
                kwargs["tools"] = tools

            response = await self.client.messages.create(**kwargs)

            # Handle tool use in response
            # If the model wants to use a tool, we return the tool use block(s) 
            # or the text content if no tool use.
            # For this simple implementation, if there's a tool use, we'll return the raw content blocks
            # and let the agent handle the loop. 
            # BUT, to keep existing agents working, we need to return a string if it's just text.
            
            # Check for tool_use
            has_tool_use = any(block.type == "tool_use" for block in response.content)
            
            if has_tool_use:
                # Return the full response object or content list so the agent can parse it
                # We'll return a special dictionary or object to signal tool use
                return {
                    "type": "tool_use",
                    "content": response.content,
                    "stop_reason": response.stop_reason
                }
            
            # Default text behavior
            text_blocks = [block.text for block in response.content if block.type == "text"]
            return "".join(text_blocks)

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
