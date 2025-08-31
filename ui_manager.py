# ui_manager.py

import sys
from typing import List, Dict, Any, Tuple
from contextlib import contextmanager
from tqdm import tqdm

from settings import Settings

class UIManager:
    """Manages all command-line interface interactions."""

    def __init__(self):
        """Initializes the UI Manager, checking if colors should be enabled."""
        self.use_colors = Settings.get('ui.enable_colors', True)
        self.colors = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "bold": "\033[1m",
            "end": "\033[0m",
        } if self.use_colors else {k: "" for k in ["blue", "green", "yellow", "red", "bold", "end"]}

    def _colorize(self, text: str, color: str) -> str:
        """Applies color formatting to text if enabled."""
        return f"{self.colors.get(color, '')}{text}{self.colors['end']}"

    def display_welcome(self):
        """Displays the welcome message and initial instructions."""
        print(self._colorize("\n--- Advanced RAG Legal Assistant ---", "bold"))
        print("Welcome! Please provide the paths or URLs to the documents you want to analyze.")
        print("You can enter multiple sources separated by commas.")
        print("Type 'help' at any time for a list of commands.\n")

    def display_help(self):
        """Displays the help menu with all available commands."""
        print(self._colorize("\nAvailable Commands:", "bold"))
        help_text = {
            "ask <question>": "Ask a question about the loaded documents.",
            "history": "Show the current session's Q&A history.",
            "docs": "List the documents that are currently loaded.",
            "summary": "Display a summary of the current session.",
            "export": "Export the session history to a JSON file.",
            "reload": "Clear the current session and load new documents.",
            "help": "Show this help message.",
            "exit / quit": "Exit the application."
        }
        for command, description in help_text.items():
            print(f"  {self._colorize(command, 'yellow'):<25} {description}")
        print()

    def get_document_sources(self) -> List[str]:
        """Prompts the user to enter document sources."""
        try:
            sources_str = input(self._colorize("Enter document paths/URLs (comma-separated): ", "blue"))
            return [source.strip() for source in sources_str.split(',') if source.strip()]
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

    def get_user_input(self) -> Tuple[str, str]:
        """Gets and parses the user's command."""
        try:
            raw_input = input(self._colorize("\n> ", "bold")).strip()
            if not raw_input:
                return "", ""
            
            parts = raw_input.split(' ', 1)
            command = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            return command, arg
        except (KeyboardInterrupt, EOFError):
            return "exit", ""

    def display_message(self, message: str, color: str = "green"):
        """Displays a generic message with optional coloring."""
        print(self._colorize(message, color))

    def display_error(self, message: str):
        """Displays an error message in red."""
        print(self._colorize(f"Error: {message}", "red"))

    def display_exit_message(self):
        """Prints a goodbye message."""
        print(self._colorize("\nThank you for using the Legal Assistant. Goodbye!", "blue"))

    def display_thinking_message(self):
        """Informs the user that the AI is processing their request."""
        print(self._colorize("\nThinking...", "yellow"))

    def display_answer(self, response: Dict[str, Any]):
        """Formats and prints the AI's answer and its sources."""
        print(self._colorize("\nAnswer:", "bold"))
        print(response.get("answer", "No answer was generated."))
        
        sources = response.get("sources", [])
        if sources:
            print(self._colorize("\nSources:", "bold"))
            unique_sources = sorted(list(set(s['source'] for s in sources)))
            for source_name in unique_sources:
                print(f"- {source_name}")
        print()

    def display_history(self, history: List[Dict[str, Any]]):
        """Displays the session's question and answer history."""
        print(self._colorize("\n--- Session History ---", "bold"))
        if not history:
            print("No questions have been asked in this session yet.")
            return
        for i, item in enumerate(history, 1):
            print(f"\n{i}. {self._colorize('Q:', 'yellow')} {item['question']}")
            print(f"   {self._colorize('A:', 'green')} {item['answer']['answer']}")
        print()
    
    def display_docs(self, doc_names: List[str]):
        """Displays the list of currently loaded documents."""
        print(self._colorize("\n--- Loaded Documents ---", "bold"))
        if not doc_names:
            print("No documents are currently loaded.")
            return
        for name in doc_names:
            print(f"- {name}")
        print()

    def display_summary(self, summary: Dict[str, Any]):
        """Displays a summary of the current session."""
        print(self._colorize("\n--- Session Summary ---", "bold"))
        print(f"  Session ID: {summary.get('session_id')}")
        print(f"  Documents Loaded: {summary.get('doc_count')}")
        print(f"  Q&A Pairs: {summary.get('qa_count')}")
        print()
    
    def confirm_action(self, prompt: str) -> bool:
        """Asks the user for a yes/no confirmation."""
        try:
            response = input(self._colorize(prompt, "yellow")).lower()
            return response in ['y', 'yes']
        except (KeyboardInterrupt, EOFError):
            return False

    @contextmanager
    def display_progress(self, description: str, total: int = 0):
        """A context manager to show a progress bar for long operations."""
        # Note: total=0 makes tqdm show progress without a defined end, useful for unknown lengths.
        # If length is known, pass it as `total`.
        with tqdm(total=total, desc=self._colorize(description, "blue"), bar_format='{l_bar}{bar}| {elapsed}') as pbar:
            yield pbar
