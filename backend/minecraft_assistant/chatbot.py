from langchain_community.chat_models import ChatOllama
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import asyncio
import os
import MessageHistory
from bot_tools.youtubeTool import youtube_tool

# Load environment variables
load_dotenv(find_dotenv())
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class AgentResponse(BaseModel):
    answer: str


def create_agent() -> AgentExecutor:
    llm = ChatOllama(model="mistral", temperature=0, base_url=OLLAMA_BASE_URL)
    
    tools = [TavilySearchResults(max_results=3), youtube_tool]

    # Get prompt and add custom instructions
    prompt = hub.pull("hwchase17/react")
    custom_instructions = f"""You are Kami, a Minecraft expert AI assistant.

Instructions:
- Use YouTubeSearch for tutorials, guides, farm builds, or Minecraft videos
- Use TavilySearchResults for recent updates or technical topics  
- Always cite sources and include links when using tools
- Provide detailed responses about Minecraft mechanics, builds, and strategies

Current date: {datetime.now().strftime("%Y-%m-%d")}"""

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

async def generate_response(query: str, session_id: str) -> AgentResponse:
    try:
        history = message_history.get_messages(session_id)
        chat_history_str = format_chat_history(history)
        
        # Include history if it exists
        input_text = f"Previous conversation:\n{chat_history_str}\n\nCurrent question: {query}" if chat_history_str else query
        
        agent = create_agent()
        result = await agent.ainvoke({"input": input_text})

        # Save to history
        message_history.add_message(session_id, {"role": "human", "content": query})
        message_history.add_message(session_id, {"role": "assistant", "content": result["output"]})

        return AgentResponse(answer=result["output"])

    except Exception as e:
        return AgentResponse(answer=f"Error processing request: {str(e)}")

# Demo usage
if __name__ == "__main__":
    async def run():
        response = await generate_response(
            "Find a recent YouTube tutorial for a Minecraft 1.20.4 netherite farm", 
            "demo-session"
        )
        print(response.answer)

    asyncio.run(run())