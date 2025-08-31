# main_updated.py

import os
import logging
# Make sure to import the updated versions of your modules
from file_handler_updated import FileHandler
from rag_pipeline_updated import RAGPipeline
from ui_manager import UIManager  # Assuming ui_manager.py needs no changes
from session_manager import SessionManager # Assuming session_manager.py needs no changes
from settings_updated import Settings

# Import the correct exception for rate limiting from the Anthropic SDK
try:
    from anthropic import RateLimitError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LegalRAGApp:
    def __init__(self):
        # --- CONSISTENCY FIX ---
        # The app is built for Anthropic, so it should check for the ANTHROPIC_API_KEY.
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set in .env file.")
        
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
            
        with self.ui.display_progress("Processing documents..."):
            documents = self.file_handler.load_documents(sources)
        
        if not documents:
            self.ui.display_error(
                "Failed to load or process any documents. Please ensure paths are correct and files are accessible."
            )
            return False

        self.rag_pipeline.build_vector_store(documents)
        self.session_manager.set_loaded_documents([doc['name'] for doc in documents])
        self.ui.display_message(f"\n✅ Successfully loaded and processed {len(documents)} document(s).", "green")
        return True

    def _main_loop(self):
        """The main interactive loop for user commands."""
        while True:
            try:
                command, arg = self.ui.get_user_input()
                
                if command in ["exit", "quit"]:
                    self.ui.display_exit_message()
                    break
                elif command == "ask":
                    self._ask_question(arg)
                elif command == "history":
                    self.ui.display_history(self.session_manager.history)
                elif command == "docs":
                    self.ui.display_docs(self.session_manager.get_loaded_documents())
                elif command == "summary":
                    self.ui.display_summary(self.session_manager.get_summary())
                elif command == "export":
                    self.session_manager.export_session()
                    self.ui.display_message(f"Session exported to session_{self.session_manager.session_id}.json", "green")
                elif command == "reload":
                    if self.ui.confirm_action("This will clear the current session. Are you sure? (y/n): "):
                        self.session_manager = SessionManager() # Re-initialize
                        if not self._load_documents():
                            return
                elif command == "help":
                    self.ui.display_help()
                else:
                    if command.lower().endswith(('.pdf', '.docx', '.txt')) or ':\\' in command or '/' in command:
                        self.ui.display_error("Unknown command. To load new documents, please use the 'reload' command.")
                    else:
                        self.ui.display_error(f"Unknown command: '{command}'. Type 'help' for a list of commands.")

            except KeyboardInterrupt:
                self.ui.display_exit_message()
                break
            except Exception as e:
                self.ui.display_error(f"An unexpected application error occurred: {e}")
                logging.error("Application crashed", exc_info=True)

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
        
        # --- BUG FIX ---
        # Replaced Google-specific 'ResourceExhausted' with Anthropic's 'RateLimitError'
        # for correct exception handling.
        except RateLimitError if ANTHROPIC_AVAILABLE else () as e:
            self.ui.display_error(
                "API rate limit exceeded for Anthropic.\n"
                "Please check your plan and billing details, then wait a moment before trying again."
            )
            logging.warning(f"Anthropic API rate limit was hit: {e}")
        except Exception as e:
            self.ui.display_error(f"An unexpected error occurred while getting an answer: {e}")
            logging.error("Question answering failed", exc_info=True)


if __name__ == "__main__":
    # This check ensures that the app only runs when the script is executed directly
    app = LegalRAGApp()
    app.run()
