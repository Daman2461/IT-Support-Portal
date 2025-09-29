from tavily import TavilyClient
from typing import Dict, Any

# Initialize Tavily client with your API key
client = TavilyClient("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")

def search_web(query: str) -> Dict[str, Any]:
    """
    Search the web using Tavily's API and return structured, relevant results.
    
    Args:
        query: The search query string
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating if the search was successful
        - results: List of search results with title, content, and URL
        - answer: Direct answer if available (from knowledge graph)
        - summary: Concise summary of the top results
    """
    try:
        # Search with enhanced parameters for better results
        response = client.search(
            query=query,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            max_results=5  # Get more results to extract better information
        )
        
        # Process and format the results
        results = []
        for result in response.get("results", [])[:3]:  # Limit to top 3 most relevant
            results.append({
                "title": result.get("title", "No title"),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "relevance": result.get("score", 0)
            })
        
        # Create a summary if no direct answer is available
        answer = response.get("answer")
        if not answer and results:
            # Extract key points from top results
            key_points = []
            for i, result in enumerate(results[:3], 1):
                key_points.append(f"{i}. {result['title']}: {result['content'][:200]}...")
            answer = "\n".join(key_points)
        
        return {
            "success": True,
            "results": results,
            "answer": answer or "No direct answer found. Here's what I found:",
            "summary": response.get("summary", "")[:500]  # Truncate long summaries
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
