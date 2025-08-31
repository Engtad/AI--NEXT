Advanced RAG Legal Assistant - Web Version
This project is a sophisticated, web-based Retrieval-Augmented Generation (RAG) application designed for legal professionals. It allows users to upload, process, and ask questions about legal documents through a simple chat interface, powered by Anthropic's Claude models.

Features
Web Interface: A clean and modern chat interface for uploading documents and asking questions.

Automatic Case Detail Extraction: The AI automatically identifies the Case Name and Case Number from uploaded documents.

Dynamic Document Loading: Load documents from your local machine with support for .pdf, .docx, and .txt files.

Configurable RAG Pipeline: Customize chunking, retrieval, and models via a config.yaml file.

Secure API Key Management: Uses a .env file to securely manage your Anthropic API key.

PDF Export: Save your entire Q&A session, including case details, to a professionally formatted PDF report.

Project Structure
legal_rag_app/
├── server.py               # Main Flask web server and API endpoints
├── index.html              # Frontend web interface
├── file_handler.py         # Handles document loading and text extraction
├── rag_pipeline.py         # Manages the core RAG logic
├── session_manager.py      # Manages session state and history
├── pdf_exporter.py         # Handles PDF generation
├── settings.py             # Loads configuration from config.yaml
├── config.yaml             # Application configuration
├── .env                    # Environment variables (API key)
├── requirements.txt        # Python dependencies
└── README.md               # This file

Setup and Installation
Clone the repository:

git clone <repository_url>
cd legal_rag_app

Create a virtual environment:

# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Set up your environment:

Rename the .env.template file to .env.

Open the .env file and add your ANTHROPIC_API_KEY.

How to Run the Web Application
Start the server:

Make sure your virtual environment is activated.

Run the server.py script from your terminal:

python server.py

Access the application:

Open your web browser and navigate to the URL shown in the terminal, which is usually:

http://127.0.0.1:5000

Troubleshooting
ImportError or ModuleNotFoundError: Your virtual environment is likely not activated, or pip install -r requirements.txt failed. Rerun the installation command.

ValueError: ANTHROPIC_API_KEY... not set: Your .env file is missing, not named correctly, or is empty.

Export Failed: PDF generation library (reportlab) not found: This means reportlab did not install correctly. Rerun pip install -r requirements.txt inside your active virtual environment.

"File not found": Ensure index.html is in the same directory as server.py.