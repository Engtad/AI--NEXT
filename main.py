import os
import logging
from file_handler import FileHandler
from rag_pipeline import RAGPipeline
from ui_manager import UIManager
from session_manager import SessionManager
from settings import Settings

class LegalRAGApp:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
        
        log_level = Settings.get('ui.log_level', 'info').upper()
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        
        self.ui = UIManager()
        self.file_handler = FileHandler()
        self.rag_pipeline = RAGPipeline(api_key=self.api_key)
        self.session_manager = SessionManager()

    def run(self):
        self.ui.display_welcome()
        
        if not self._load_documents():
            return

        self._main_loop()

    def _load_documents(self) -> bool:
        """Handles the document loading flow."""
        sources = self.ui.get_document_sources()
        if not sources:
            self.ui.display_error("No documents provided. Exiting.")
            return False
            
        documents = self.file_handler.load_documents(sources)
        
        if not documents:
            self.ui.display_error("Failed to load or process documents.")
            return False

        self.rag_pipeline.build_vector_store(documents)
        self.session_manager.set_loaded_documents([doc['name'] for doc in documents])
        self.ui.display_message(f"\n✅ Successfully loaded {len(documents)} document(s).", "green")
        return True

    def _main_loop(self):
        """The main interactive loop for user commands."""
        while True:
            command, arg = self.ui.get_user_input()
            
            if command in ["exit", "quit"]:
                self.ui.display_exit_message()
                break
            elif command == "ask":
                self._ask_question(arg)
            elif command == "history":
                self.ui.display_history(self.session_manager.get_history())
            elif command == "docs":
                self.ui.display_docs(self.session_manager.get_loaded_documents())
            elif command == "summary":
                self.ui.display_summary(self.session_manager.get_summary())
            elif command == "export":
                self._export_session() # --- UPDATED: Use a dedicated method
            elif command == "reload":
                if self.ui.confirm_action("This will clear session. Are you sure? (y/n): "):
                    self.session_manager.start_new_session()
                    if not self._load_documents():
                        break
            elif command == "help":
                self.ui.display_help()
            else:
                self.ui.display_error(f"Unknown command: '{command}'. Type 'help' for assistance.")

    def _export_session(self):
        """Handles the logic for exporting the session to JSON or PDF."""
        export_format = self.ui.get_export_format()
        if not export_format:
            return

        if export_format == 'json':
            filepath = self.session_manager.export_to_json()
            if filepath:
                self.ui.display_message(f"Session exported to {filepath}", "green")
            else:
                self.ui.display_error("Failed to export session to JSON.")
        
        elif export_format == 'pdf':
            case_details = self.ui.get_case_details()
            filepath = self.session_manager.export_to_pdf(case_details)
            if filepath:
                self.ui.display_message(f"Session exported to {filepath}", "green")
            else:
                self.ui.display_error("Failed to export session to PDF. Is 'reportlab' installed?")

    def _ask_question(self, question: str):
        if not question:
            self.ui.display_error("Please provide a question after the 'ask' command.")
            return

        self.ui.display_thinking_message()
        try:
            response = self.rag_pipeline.answer_question(question)
            if response:
                self.session_manager.add_qa_pair(question, response)
                self.ui.display_answer(response)
        except Exception as e:
            self.ui.display_error(f"An unexpected error occurred: {e}")
            logging.error("Question answering failed", exc_info=True)

if __name__ == "__main__":
    try:
        app = LegalRAGApp()
        app.run()
    except Exception as e:
        logging.fatal(f"A critical error occurred: {e}", exc_info=True)
