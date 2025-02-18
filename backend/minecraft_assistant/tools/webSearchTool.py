from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.tools import tool
from langchain.chains import LLMChain
from tavily import TavilyClient
from dotenv import load_dotenv, find_dotenv
import os
from typing import Dict, Any

# Find and Load Environment Variables
load_dotenv(find_dotenv())
tavily = TavilyClient(api_key=os.environ['TAVILYAI_API_KEY'])

def lookup(query: str) -> Dict[str, Any]:
    """Perform a Tavily search with advanced depth."""
    return tavily.search(query, search_depth='advanced',max_results=5)

@tool
def tavilySearchTool(query: str) -> str:
    """Search for Minecraft-related information using Tavily search."""
    search_results = lookup(query)
    
    summary_template = """
    Based on the following search results, provide a helpful answer about Minecraft:
    {information}
    
    Focus on providing accurate information with sources when available.
    """
    
    summary_prompt = PromptTemplate(
        input_variables=["information"],
        template=summary_template
    )
    
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4-turbo",
        api_key=os.environ['OPENAI_API_KEY']
    )
    
    chain = LLMChain(llm=llm, prompt=summary_prompt)
    result = chain.invoke({"information": search_results})
    return result["text"]