from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, AIMessage
from langchain import hub
from tools import youtubeTool
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import asyncio
import os
import MessageHistory

# Load environment variables
load_dotenv(find_dotenv())
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Pydantic schema for API response
class AgentResponse(BaseModel):
    answer: str

current_date = datetime.now().strftime("%Y-%m-%d")

# Create LangChain agent with tools
def create_agent() -> AgentExecutor:
    llm = ChatOllama(model="mistral", temperature=0, base_url=OLLAMA_BASE_URL)
    tools = [TavilySearchResults(max_results=3), youtubeTool.youtube_tool]

    # Use LangChain's built-in ReAct prompt
    prompt = hub.pull("hwchase17/react")
    
    # Customize the system message
    custom_instructions = f"""You are Kami, a Minecraft expert AI assistant.

You can use tools such as YouTubeSearch and TavilySearchResults to find accurate and recent information.

Instructions:
- Use the YouTubeSearch tool if the user wants a tutorial, guide, farm build, or Minecraft video.
- Use TavilySearchResults for recent updates or obscure technical topics.
- If you use tools, clearly cite sources or include links in the answer.
- If you know the answer with certainty, you may respond directly.

Current date: {current_date}

"""

    # Add custom instructions to the existing prompt
    prompt = prompt.partial(instructions=custom_instructions)

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Maintain chat history by session
message_history = MessageHistory.MessageHistory()

# Helper function to format chat history as string
def format_chat_history(history):
    if not history:
        return ""
    
    formatted = []
    for msg in history:
        if msg["role"] == "human":
            formatted.append(f"Human: {msg['content']}")
        elif msg["role"] == "assistant":
            formatted.append(f"Assistant: {msg['content']}")
    
    return "\n".join(formatted)

# Main agent execution logic
async def generate_response(query: str, session_id: str) -> AgentResponse:
    try:
        history = message_history.get_messages(session_id)
        
        # Format history as string for ReAct agent
        chat_history_str = format_chat_history(history)
        
        # If there's chat history, prepend it to the input
        if chat_history_str:
            input_with_history = f"Previous conversation:\n{chat_history_str}\n\nCurrent question: {query}"
        else:
            input_with_history = query

        agent = create_agent()
        
        result = await agent.ainvoke({
            "input": input_with_history
        })

        # Log conversation
        message_history.add_message(session_id, {"role": "human", "content": query})
        message_history.add_message(session_id, {"role": "assistant", "content": result["output"]})

        return AgentResponse(answer=result["output"])

    except Exception as e:
        import traceback
        traceback.print_exc()
        return AgentResponse(answer=f"Error: {str(e)}")

# Alternative approach using a custom prompt template
def create_agent_custom_prompt() -> AgentExecutor:
    llm = ChatOllama(model="mistral", temperature=0, base_url=OLLAMA_BASE_URL)
    tools = [TavilySearchResults(max_results=3), youtubeTool.youtube_tool]

    # Custom ReAct prompt template
    template = f"""You are Kami, a Minecraft expert AI assistant.

You can use tools such as YouTubeSearch and TavilySearchResults to find accurate and recent information.

Instructions:
- Use the YouTubeSearch tool if the user wants a tutorial, guide, farm build, or Minecraft video.
- Use TavilySearchResults for recent updates or obscure technical topics.
- If you use tools, clearly cite sources or include links in the answer.
- If you know the answer with certainty, you may respond directly.

Current date: {current_date}

TOOLS:
------

You have access to the following tools:

{{tools}}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Question: {{input}}
Thought:{{agent_scratchpad}}"""

    prompt = PromptTemplate.from_template(template)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Demo/test usage
if __name__ == "__main__":
    session_id = "demo-session"

    async def run():
        question = "Find a recent YouTube tutorial for a Minecraft 1.20.4 netherite farm"
        response = await generate_response(question, session_id)
        print("Structured Output:\n", response.model_dump())

    asyncio.run(run())