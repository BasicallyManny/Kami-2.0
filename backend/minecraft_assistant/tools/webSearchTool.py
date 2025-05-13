from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.tools import tool
from langchain.chains import LLMChain
from tavily import TavilyClient
from dotenv import load_dotenv, find_dotenv
import os
from typing import Dict, Any, List

# Find and Load Environment Variables
load_dotenv(find_dotenv())
tavily = TavilyClient(api_key=os.environ['TAVILYAI_API_KEY'])

def lookup(query: str) -> Dict[str, Any]:
    """Perform a Tavily search with advanced depth."""
    return tavily.search(query, search_depth='advanced', max_results=7)

@tool
def tavilySearchTool(query: str) -> str:
    """
    Search for Minecraft-related information and return relevant URLs that help answer the query.
    This tool focuses on finding authoritative sources rather than providing direct answers.
    """
    # Enhance the query to focus on Minecraft if not already specified
    if "minecraft" not in query.lower():
        search_query = f"Minecraft {query}"
    else:
        search_query = query
    
    # Get search results
    search_results = lookup(search_query)
    
    # Extract useful information from results
    sources = []
    for result in search_results.get("results", []):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        snippet = result.get("content", "")[:150] + "..." if result.get("content") else ""
        
        # Only include results that seem relevant (basic filtering)
        if url and (
            ".minecraft.net" in url or 
            "minecraft" in url.lower() or 
            "minecraft" in title.lower() or
            "minecraft" in snippet.lower()
        ):
            sources.append({
                "title": title,
                "url": url,
                "snippet": snippet
            })
    
    # Use LLM to rank and filter the most relevant URLs for the specific query
    ranking_template = """
    Given the user's Minecraft-related query: "{query}"
    
    Review these search results and identify the URLs that would be MOST HELPFUL in answering this specific question.
    Focus only on selecting the most relevant sources - do not answer the question directly.
    
    Search results:
    {search_results}
    
    Return ONLY a list of the most relevant URLs in order of relevance, with a brief explanation of why each source is helpful.
    Format your response as:
    1. [URL] - Brief reason this source is relevant
    2. [URL] - Brief reason this source is relevant
    etc.
    
    If no sources seem relevant, explain why and suggest a better search query.
    """
    
    ranking_prompt = PromptTemplate(
        input_variables=["query", "search_results"],
        template=ranking_template
    )
    
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4-turbo",
        api_key=os.environ['OPENAI_API_KEY']
    )
    
    chain = LLMChain(llm=llm, prompt=ranking_prompt)
    
    # Convert sources to formatted text for the LLM
    source_text = ""
    for idx, source in enumerate(sources, 1):
        source_text += f"{idx}. Title: {source['title']}\n   URL: {source['url']}\n   Preview: {source['snippet']}\n\n"
    
    if not source_text:
        return "No relevant Minecraft sources found. Try refining your search query to be more specific."
    
    # Get ranked URLs
    result = chain.invoke({
        "query": query,
        "search_results": source_text
    })
    
    return result["text"]
