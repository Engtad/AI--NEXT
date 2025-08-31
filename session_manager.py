import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import the PDFExporter, which is in a different file
from pdf_exporter import PDFExporter, REPORTLAB_AVAILABLE

class SessionManager:
    """Manages session state, history, and exporting."""

    def __init__(self):
        self.start_new_session()

    def start_new_session(self):
        """Resets the session to its initial state."""
        self.session_id = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        self.history: List[Dict[str, Any]] = []
        self.loaded_docs: List[str] = []

    def add_qa_pair(self, question: str, response: Dict[str, Any]):
        """Adds a question and its corresponding answer to the session history."""
        self.history.append({"question": question, "answer": response})

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns the full Q&A history."""
        return self.history

    def set_loaded_documents(self, doc_names: List[str]):
        """Sets the list of loaded document names."""
        self.loaded_docs = doc_names

    def get_loaded_documents(self) -> List[str]:
        """Returns the list of loaded document names."""
        return self.loaded_docs

    def get_summary(self) -> Dict[str, Any]:
        """Provides a summary of the current session."""
        return {
            "session_id": self.session_id,
            "document_count": len(self.loaded_docs),
            "qa_pairs_count": len(self.history),
            "documents": self.loaded_docs
        }

    def export_to_json(self) -> Optional[str]:
        """Exports the session summary and history to a JSON file."""
        filepath = f"{self.session_id}.json"
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.get_summary(), f, indent=4)
            return filepath
        except Exception:
            return None

    def export_to_pdf(self, case_details: Dict[str, str]) -> Optional[str]:
        """Exports the session Q&A history to a PDF report."""
        if not REPORTLAB_AVAILABLE:
            return None
            
        filepath = f"case_report_{self.session_id}.pdf"
        try:
            exporter = PDFExporter(
                history=self.history,
                case_details=case_details,
                output_path=filepath
            )
            exporter.generate_pdf()
            return filepath
        except Exception:
            return None
