from typing import List, Dict, Any

class MessageHistory:
    """Message history manager for maintaining conversation context."""
    
    def __init__(self):
        self.history: Dict[str, List[Dict[str, Any]]] = {}
        
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get message history for a session."""
        return self.history.get(session_id, [])
        
    def add_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Add a message to the session history."""
        if session_id not in self.history:
            self.history[session_id] = []
        self.history[session_id].append(message)