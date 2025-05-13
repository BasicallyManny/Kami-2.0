from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from dotenv import load_dotenv, find_dotenv
import asyncio
import os
import MessageHistory

# Import the web search tool
from langchain_community.tools.tavily_search import TavilySearchResults

# Load environment variables
load_dotenv(find_dotenv())

def create_agent(system_prompt):
    """Main Agent Executor"""
    
    # Initialize chat model
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",  # Use "gpt-4" or other models as needed
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Define available tools
    tools = [TavilySearchResults(max_results=3)]
    
    # Create a Minecraft-focused prompt template with more structured input handling
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        human_message_prompt,
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # Create agent executor
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
        
        # Create agent with current context
        agent_executor = create_agent(system_prompt)
        
        # Prepare chat history for the agent
        formatted_history = []
        for msg in current_history:
            role = "ai" if msg["role"] == "assistant" else msg["role"]
            formatted_history.append((role, msg["content"]))
        
        # Get response
        response = await agent_executor.ainvoke({
            "input": query,
            "chat_history": formatted_history
        })
        
        # Store the messages
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
    
    # Define a Minecraft-specialized system prompt using PromptTemplate
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
    
    # Format the system prompt template with current date
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    system_prompt = system_prompt_template.format(current_date=current_date)
    
    async def run_example():
        # Example 1: Minecraft-specific question
        query1 = "How do I find netherite in Minecraft?"
        print(f"Q1: {query1}")
        response1 = await generate_response(
            query1, 
            session_id,
            system_prompt
        )
        print(f"A1: {response1}\n")
        
        # Example 2: Follow-up question to show context awareness
        query2 = "What tools should I use to mine it efficiently?"
        print(f"Q2: {query2}")
        response2 = await generate_response(query2, session_id)
        print(f"A2: {response2}")
    
    # Run the example
    asyncio.run(run_example())