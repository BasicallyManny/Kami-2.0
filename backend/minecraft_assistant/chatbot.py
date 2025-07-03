from langchain_community.chat_models import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
import re
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import asyncio
import os
import MessageHistory
from bot_tools.youtubeTool import youtube_tool
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
- Use YouTubeSearch for tutorials, guides, farm builds, or Minecraft videos
- Use TavilySearchResults for recent updates or technical topics
- Provide detailed responses about Minecraft mechanics, builds, and strategies
- When providing your final answer, focus on summarizing the key information and concepts rather than listing specific URLs
- Present information in a clear, educational format that helps users understand the topic"""

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

def clean_urls_from_text(text: str) -> str:
    """Remove URLs from text and clean up formatting"""
    # Remove URLs
    url_pattern = r'https?://[^\s\n<>)(\]]+(?=[\s\n<>)(\]]|$)'
    cleaned_text = re.sub(url_pattern, '', text)
    
    # Clean up extra whitespace and formatting issues
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Multiple spaces to single space
    cleaned_text = re.sub(r'[\n\r]+', '\n', cleaned_text)  # Multiple newlines to single
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)  # Clean paragraph breaks
    cleaned_text = cleaned_text.strip()
    
    # Remove common artifacts left after URL removal
    cleaned_text = re.sub(r'\s*[-–—]\s*$', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'^\s*[-–—]\s*', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'\s*:\s*$', '', cleaned_text, flags=re.MULTILINE)
    
    return cleaned_text

def generalize_answer(text: str) -> str:
    """Further process the answer to make it more generalized"""
    # Remove references to specific search results
    text = re.sub(r'based on the search results?[,.]?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'according to the search results?[,.]?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'from the search results?[,.]?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'the search results? show[s]?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'i found[^.]*?\.\s*', '', text, flags=re.IGNORECASE)
    
    # Remove references to specific videos/sources without context
    text = re.sub(r'check out this video[^.]*?\.\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'watch this tutorial[^.]*?\.\s*', '', text, flags=re.IGNORECASE)
    
    # Clean up sentences that might be incomplete after URL removal
    sentences = text.split('.')
    cleaned_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Keep sentences that are substantial
            # Check if sentence ends abruptly (common after URL removal)
            if not sentence.endswith((':', 'at', 'on', 'in', 'by', 'from', 'to', 'for')):
                cleaned_sentences.append(sentence)
    
    return '. '.join(cleaned_sentences) + ('.' if cleaned_sentences else '')

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
        
        # Clean URLs from answer and generalize it
        cleaned_answer = clean_urls_from_text(raw_answer)
        generalized_answer = generalize_answer(cleaned_answer)
        
        # Save original query and generalized answer to history
        message_history.add_message(session_id, {"role": "human", "content": query})
        message_history.add_message(session_id, {"role": "assistant", "content": generalized_answer})
        
        return ChatResponse(answer=generalized_answer, urls=urls)
    
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        return ChatResponse(answer=error_msg, urls=[])

# Demo usage
if __name__ == "__main__":
    async def run():
        response = await generate_response(
            "How do I build an automatic sugar cane farm in Minecraft?", 
            "demo-session"
        )
        print("Answer:", response.answer)
        print("URLs found:", response.urls)
    
    asyncio.run(run())