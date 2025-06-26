from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import asyncio
import os
import MessageHistory

# Load environment variables
load_dotenv(find_dotenv())
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Pydantic output schema
class AgentResponse(BaseModel):
    answer: str

# Create Minecraft-specific system prompt
system_prompt_template = PromptTemplate.from_template(
    """You are Kami, a Minecraft expert AI assistant.
    Use deep Minecraft knowledge to answer questions clearly.
    Use search tools only for new/obscure topics or recent updates.
    Cite sources if tools are used.
    Current date: {current_date}"""
)
current_date = datetime.now().strftime("%Y-%m-%d")
system_prompt = system_prompt_template.format(current_date=current_date)

# Create agent
def create_agent(system_prompt: str) -> AgentExecutor:
    llm = ChatOllama(model="mistral", temperature=0, base_url=OLLAMA_BASE_URL)
    tools = [TavilySearchResults(max_results=3)]
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Track chat history
message_history = MessageHistory.MessageHistory()

# Query the agent
async def generate_response(query: str, session_id: str) -> AgentResponse:
    try:
        history = message_history.get_messages(session_id)
        formatted = [
            ("ai" if msg["role"] == "assistant" else msg["role"], msg["content"])
            for msg in history
        ]
        agent = create_agent(system_prompt)
        result = await agent.ainvoke({"input": query, "chat_history": formatted})

        # Store conversation
        message_history.add_message(session_id, {"role": "human", "content": query})
        message_history.add_message(session_id, {"role": "assistant", "content": result["output"]})

        return AgentResponse(answer=result["output"])

    except Exception as e:
        return AgentResponse(answer=f"Error: {str(e)}")

# Example use
if __name__ == "__main__":
    session_id = "demo-session"

    async def run():
        question = "How do I find netherite in Minecraft?"
        response = await generate_response(question, session_id)
        print("Structured Output:\n", response.model_dump())

    asyncio.run(run())
