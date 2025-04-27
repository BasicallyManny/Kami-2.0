from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor
from langchain.agents import create_openai_tools_agent
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any

# Import tools from separate file
from tools.webSearchTool import tavilySearchTool

# Load environment variables
load_dotenv(find_dotenv())

class MessageHistory:
    """Message history manager."""
    def __init__(self):
        self.history: Dict[str, List[Dict[str, Any]]] = {}
    
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get message history for a session."""
        return self.history.get(session_id, [])
    
    def add_messages(self, session_id: str, message: Dict[str, Any]) -> None:
        """Add a message to the session history."""
        if session_id not in self.history:
            self.history[session_id] = []
        self.history[session_id].append(message)

# Initialize chat model
chat = ChatOpenAI(
    model="gpt-3.5-turbo",  # Change from "gpt-4-turbo" to "gpt-4" if you don’t have access
    temperature=0
)

# Define available tools
tools = [tavilySearchTool]

# Initialize message history
message_history = MessageHistory()

async def generate_response(query: str, chat_session_token: str) -> str:
    """Generate a response using the agent."""
    try:
        # Get current chat history
        current_history = message_history.get_messages(chat_session_token)

        # Ensure messages are formatted correctly
        formatted_history = [(msg["role"], msg["content"]) for msg in current_history]

        # Create prompt template with current history
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Minecraft Assistant. You help users with Minecraft-related questions by providing accurate information and useful resources."),
            *formatted_history,
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent with current context
        agent = create_openai_tools_agent(chat, tools, prompt)

        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )

        # Get response
        response = await agent_executor.ainvoke({"input": query})

        # Store the messages
        message_history.add_messages(chat_session_token, {"role": "human", "content": query})
        message_history.add_messages(chat_session_token, {"role": "assistant", "content": response["output"]})

        return response["output"]
    
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(error_msg)
        return error_msg
    
#test the function
if __name__ == "__main__":
    import asyncio
    session_id = "test_session"
    query = "What is the best way to find diamonds in Minecraft?"
    try:
        response = asyncio.run(generate_response(query, session_id))
        print(response)
    except Exception as e:
        print(f"Error: {str(e)}")
