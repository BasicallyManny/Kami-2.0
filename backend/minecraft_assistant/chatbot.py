from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.agents import AgentExecutor, create_openai_functions_agent
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
import MessageHistory
from langchain_community.tools.tavily_search import TavilySearchResults
from datetime import datetime

# Load .env variables
load_dotenv(find_dotenv())
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def create_agent(system_prompt):
    llm = ChatOllama(model="mistral", temperature=0, base_url=OLLAMA_BASE_URL)
    tools = [TavilySearchResults(max_results=3)]
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        human_message_prompt,
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

message_history = MessageHistory.MessageHistory()

async def generate_response(query, session_id, system_prompt):
    history = message_history.get_messages(session_id)
    formatted = [("ai" if m["role"] == "assistant" else m["role"], m["content"]) for m in history]
    agent_executor = create_agent(system_prompt)
    result = await agent_executor.ainvoke({
        "input": query,
        "chat_history": formatted
    })
    message_history.add_message(session_id, {"role": "human", "content": query})
    message_history.add_message(session_id, {"role": "assistant", "content": result["output"]})
    return result["output"]

if __name__ == "__main__":
    session_id = "test_session"
    template = PromptTemplate.from_template(
        """You are Kami, a Minecraft expert assistant. Use Minecraft-specific knowledge to answer questions.
        Use tools only when the answer is unknown or outdated. Cite sources from web searches if used.
        Current date: {current_date}"""
    )
    current_date = datetime.now().strftime("%Y-%m-%d")
    system_prompt = template.format(current_date=current_date)

    async def run():
        q1 = "How do I find netherite in Minecraft?"
        print(f"Q: {q1}")
        print("A:", await generate_response(q1, session_id, system_prompt))
        q2 = "What tool should I use to mine it?"
        print(f"Q: {q2}")
        print("A:", await generate_response(q2, session_id, system_prompt))

    asyncio.run(run())
