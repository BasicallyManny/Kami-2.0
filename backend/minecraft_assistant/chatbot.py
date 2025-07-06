from langchain_community.chat_models import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
import re
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
from minecraft_assistant import MessageHistory
from minecraft_assistant.bot_tools.youtubeTool import youtube_tool
from pydantic import BaseModel
from typing import Optional

# Load environment variables
load_dotenv(find_dotenv())
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


class ChatResponse(BaseModel):
    answer: Optional[str] = None
    urls: Optional[list[str]] = None

def create_agent() -> AgentExecutor:
    llm = ChatOllama(model="mistral", temperature=0, base_url=OLLAMA_BASE_URL)
    
    tools = [TavilySearchResults(max_results=3), youtube_tool]
    
    # Get prompt and add custom instructions
    prompt = hub.pull("hwchase17/react")
    custom_instructions = f"""You are Kami, a Minecraft expert AI assistant.

Instructions:
- You are a Web Search Agent for Minecraft-related queries.
- Use YouTubeSearch for tutorials, guides, farm builds, or Minecraft videos with URLS
- Use TavilySearchResults for recent updates or technical topics with URLS
- Present answers in a clear, concise manner with relevant URLs.
"""

    prompt = prompt.partial(instructions=custom_instructions)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Chat history management
message_history = MessageHistory.MessageHistory()

def format_chat_history(history):
    if not history:
        return ""
    
    formatted = []
    for msg in history:
        role = "Human" if msg["role"] == "human" else "Assistant"
        formatted.append(f"{role}: {msg['content']}")
    
    return "\n".join(formatted)

def extract_urls_from_text(text: str) -> list[str]:
    """Extract URLs from text using regex"""
    url_pattern = r'https?://[^\s\n<>)(\]]+(?=[\s\n<>)(\]]|$)'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # Remove duplicates

async def generate_response(query: str, session_id: str) -> ChatResponse:
    try:
        history = message_history.get_messages(session_id)
        chat_history_str = format_chat_history(history)
        
        # Include history if it exists
        input_text = f"Previous conversation:\n{chat_history_str}\n\nCurrent question: {query}" if chat_history_str else query
        
        agent = create_agent()
        result = await agent.ainvoke({"input": input_text})
        
        # Extract URLs first
        raw_answer = result["output"]
        urls = extract_urls_from_text(raw_answer)
        
        # Save original query and generalized answer to history
        message_history.add_message(session_id, {"role": "human", "content": query})
        message_history.add_message(session_id, {"role": "assistant", "content": raw_answer})
        
        return ChatResponse(answer=raw_answer, urls=urls)
    
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        return ChatResponse(answer=error_msg, urls=[])
         