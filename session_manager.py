import json
import logging
from datetime import datetime
from typing import List, Dict, Any

class SessionManager:
    """Manages session data, including history and loaded documents."""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.history: List[Dict[str, Any]] = []
        self.loaded_documents: List[str] = []

    def set_loaded_documents(self, doc_names: List[str]):
        """Sets the list of loaded document names for the session."""
        self.loaded_documents = doc_names

    def add_qa_pair(self, question: str, answer: Dict[str, Any]):
        """Adds a question and its answer to the session history."""
        self.history.append({"question": question, "answer": answer})

    def get_summary(self) -> Dict[str, Any]:
        """Returns a summary of the current session."""
        return {
            "session_id": self.session_id,
            "doc_count": len(self.loaded_documents),
            "doc_names": self.loaded_documents,
            "qa_count": len(self.history)
        }

    def export_session(self, export_path: str = "") -> bool:
        """Exports the session history to a JSON file."""
        if not export_path:
            export_path = f"session_{self.session_id}.json"
        
        try:
            with open(export_path, 'w') as f:
                json.dump({
                    "session_id": self.session_id,
                    "documents": self.loaded_documents,
                    "history": self.history
                }, f, indent=4)
            return True
        except IOError as e:
            logging.error(f"Failed to export session to '{export_path}': {e}")
            return False

