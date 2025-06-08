from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.agents import AgentExecutor, create_openai_functions_agent
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
import MessageHistory

# Import the web search tool
from langchain_community.tools.tavily_search import TavilySearchResults

# Load environment variables
load_dotenv(find_dotenv())

def create_agent(system_prompt):
    """Main Agent Executor using Ollama"""
    
    # Load Ollama model (e.g., mistral, phi, llama3)
    llm = ChatOllama(
        model="mistral",  # Change this if you want to try llama3, phi, etc.
        temperature=0
    )
    
    # Define tools
    tools = [TavilySearchResults(max_results=3)]
    
    # Prompt structure
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        human_message_prompt,
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Use create_openai_functions_agent for Ollama-compatible tools agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Wrap with executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor

# Initialize message history
message_history = MessageHistory.MessageHistory()

async def generate_response(query: str, session_id: str, system_prompt: str = "You are a helpful AI assistant.") -> str:
    """Generate a response using the agent."""
    try:
        # Get current chat history
        current_history = message_history.get_messages(session_id)
        
        # Create agent
        agent_executor = create_agent(system_prompt)
        
        # Format history
        formatted_history = []
        for msg in current_history:
            role = "ai" if msg["role"] == "assistant" else msg["role"]
            formatted_history.append((role, msg["content"]))
        
        # Invoke agent
        response = await agent_executor.ainvoke({
            "input": query,
            "chat_history": formatted_history
        })
        
        # Store messages
        message_history.add_message(session_id, {"role": "human", "content": query})
        message_history.add_message(session_id, {"role": "assistant", "content": response["output"]})
        
        return response["output"]
        
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(error_msg)
        return error_msg

# Example usage
if __name__ == "__main__":
    session_id = "test_session"
    
    # Define system prompt
    system_prompt_template = PromptTemplate.from_template(
        """You are Kami, a specialized AI assistant that provides accurate and helpful information about Minecraft.
        
        Your expertise includes:
        - Minecraft gameplay mechanics, crafting recipes, and redstone circuits
        - Different game versions, updates, and their features
        - Mods, resource packs, and data packs
        - Technical information about servers, commands, and game optimization
        - Community builds, farms, and common game strategies
        
        When answering questions:
        1. Prioritize Minecraft-specific knowledge and terminology
        2. If you know the answer from your training, respond clearly and accurately
        3. For recent updates or complex technical details, use the search tools provided
        4. Always cite sources when using search results
        5. When suggesting builds or techniques, consider the player's potential experience level
        6. For version-specific information, clarify which Minecraft version you're referring to
        
        Current date: {current_date}
        """
    )
    
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    system_prompt = system_prompt_template.format(current_date=current_date)
    
    async def run_example():
        query1 = "How do I find netherite in Minecraft?"
        print(f"Q1: {query1}")
        response1 = await generate_response(query1, session_id, system_prompt)
        print(f"A1: {response1}\n")
        
        query2 = "What tools should I use to mine it efficiently?"
        print(f"Q2: {query2}")
        response2 = await generate_response(query2, session_id)
        print(f"A2: {response2}")
    
    asyncio.run(run_example())
