Advanced RAG Legal Assistant
This project is a sophisticated, command-line based Retrieval-Augmented Generation (RAG) application designed for legal professionals. It allows users to load, process, and ask questions about legal documents using the power of Google's Gemini large language models.

This enhanced version includes session management, a rich interactive command interface, advanced error handling, and a configurable RAG pipeline.

Features
Interactive Command Interface: Control the application with simple commands (ask, history, docs, reload, exit).

Dynamic & Secure Document Loading: Load documents from local paths or URLs with progress bars, validation, and robust error handling.

Multi-Format Support: Handles .pdf, .docx, and .txt files.

Configurable RAG Pipeline: Customize chunking, retrieval parameters, and models via a config.yaml file.

Secure API Key Management: Uses a .env file to securely manage your Google API key.

Session Management: View question history, list loaded docs, and export your entire session to a JSON file.

Enhanced Responses: Get answers with source citations and a confidence score.

Query Caching: Speeds up responses for repeated questions.

Production-Ready Architecture: Modular, decoupled components for easy maintenance and extension.

Project Structure
legal_rag_app/
├── main.py                   # Main application entry point and command handler
├── file_handler.py           # Handles document loading and text extraction
├── rag_pipeline.py           # Manages the core RAG logic (embedding, vector store, QA chain)
├── ui_manager.py             # Manages the command-line user interface
├── session_manager.py        # Manages session state, history, and exporting
├── settings.py               # Loads configuration from config.yaml and .env
├── config.yaml.template      # Template for application configuration
├── .env.template             # Template for environment variables (API key)
└── README.md                 # This file

Setup and Installation
Clone the repository:

git clone <repository_url>
cd legal_rag_app

Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install dependencies from requirements.txt:

pip install -r requirements.txt

Set up your environment:

Copy the .env.template file to a new file named .env.

Open the .env file and add your Google API key.

GOOGLE_API_KEY="your_api_key_here"

Configure the application (Optional):

Copy config.yaml.template to config.yaml.

Edit config.yaml to set your desired models, chunking strategy, etc.

How to Run
Execute the main script:

python main.py

The application will automatically find your API key in the .env file. If it doesn't, it will prompt you to enter it manually.

Interact with the assistant:

Provide comma-separated paths or URLs to your legal documents.

Once documents are processed, type help to see all available commands.

Start asking questions using ask <your question here>.

Troubleshooting
"Failed to initialize AI models": Your Google API key in the .env file may be invalid or have insufficient permissions.

"File not found": Double-check your local file paths. For URLs, ensure they are accessible and correct.

"No content extracted": The document might be image-based (scanned) or empty. This version does not support OCR for scanned documents.