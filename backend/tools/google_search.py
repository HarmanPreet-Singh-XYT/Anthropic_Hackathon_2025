"""
Google Custom Search Tool
Allows agents to perform web searches using Google's Custom Search JSON API
"""

from typing import Dict, Any, List, Optional
from googleapiclient.discovery import build
from config.settings import settings

class GoogleSearchTool:
    """
    Tool for performing Google searches
    """
    
    def __init__(self):
        """Initialize Google Search service"""
        if not settings.google_api_key or not settings.google_cse_id:
            print("⚠ Google Search keys not found in settings")
            self.service = None
        else:
            try:
                self.service = build(
                    "customsearch", 
                    "v1", 
                    developerKey=settings.google_api_key
                )
            except Exception as e:
                print(f"⚠ Failed to initialize Google Search: {e}")
                self.service = None

    @property
    def tool_definition(self) -> Dict[str, Any]:
        """
        Get Anthropic tool definition
        """
        return {
            "name": "google_search",
            "description": "Search Google for information about scholarships, organizations, or specific topics to verify claims or get more context.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to execute"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 3, max 10)",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }

    async def execute(self, query: str, num_results: int = 3) -> str:
        """
        Execute a Google search
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Formatted string of search results
        """
        if not self.service:
            return "Error: Google Search is not configured."

        print(f"  🔍 Google Search: '{query}'")
        
        try:
            # Execute search
            res = self.service.cse().list(
                q=query,
                cx=settings.google_cse_id,
                num=min(num_results, 10)
            ).execute()
            
            items = res.get("items", [])
            
            if not items:
                return f"No results found for '{query}'."
            
            # Format results
            formatted_results = []
            for i, item in enumerate(items, 1):
                title = item.get("title", "No title")
                snippet = item.get("snippet", "No snippet")
                link = item.get("link", "")
                
                formatted_results.append(
                    f"Result {i}:\n"
                    f"Title: {title}\n"
                    f"Snippet: {snippet}\n"
                    f"Link: {link}\n"
                )
                
            return "\n".join(formatted_results)
            
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            print(f"  ❌ {error_msg}")
            return error_msg
