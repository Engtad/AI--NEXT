import os
import logging
import json
from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from io import BytesIO
from dotenv import load_dotenv

# --- Load environment variables from .env file ---
load_dotenv()

# Import your existing application logic
from file_handler import FileHandler
from rag_pipeline import RAGPipeline
from session_manager import SessionManager
from settings import Settings
from pdf_exporter import PDFExporter

# --- Initial Setup ---
# Load API Key from .env
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set. Please check your .env file.")

# Configure logging using settings from config.yaml
log_level = Settings.get('ui.log_level', 'info').upper()
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Initialize Core Components ---
file_handler = FileHandler()
rag_pipeline = RAGPipeline(api_key=api_key)
session_manager = SessionManager()

# Define the upload folder
UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Web Server Routes ---

@app.route('/')
def index():
    """Serves the main index.html file."""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return "index.html not found", 404

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handles file uploads, extracts case details, and builds the vector store."""
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400

    filepaths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        filepaths.append(filepath)

    try:
        documents = file_handler.load_documents(filepaths)
        if not documents:
            return jsonify({"error": "Could not extract content from the documents."}), 500
            
        rag_pipeline.build_vector_store(documents)
        session_manager.start_new_session()
        session_manager.set_loaded_documents([doc['name'] for doc in documents])

        # --- Logic to extract case details ---
        extracted_details = {"caseName": "N/A", "caseNumber": "N/A"}
        if documents:
            first_doc_content = documents[0].get('content', '')[:4000]
            
            prompt = f"""
            From the following legal document text, identify the Case Name and the Case Number.
            - The Case Name is typically in the format 'Plaintiff v. Defendant'.
            - The Case Number might be labeled 'No.', 'Case No.', 'Docket No.', etc.
            Return the answer ONLY as a valid JSON object with the keys "caseName" and "caseNumber".
            If a value is not found, use "N/A".

            Document Text:
            "{first_doc_content}"
            """
            
            try:
                response = rag_pipeline.llm.invoke(prompt)
                details_str = response.content
                
                # --- More robust JSON extraction ---
                start_index = details_str.find('{')
                end_index = details_str.rfind('}')
                
                if start_index != -1 and end_index != -1 and end_index > start_index:
                    json_str = details_str[start_index : end_index + 1]
                    extracted_details = json.loads(json_str)
                else:
                    logging.warning(f"LLM did not return a valid JSON object for case details. Response: {details_str}")
                    extracted_details = {"caseName": "N/A", "caseNumber": "N/A"}

            except Exception as e:
                logging.error(f"Could not extract or parse case details from LLM: {e}")
                extracted_details = {"caseName": "N/A", "caseNumber": "N/A"}

        # Clean up uploaded files after processing
        for path in filepaths:
            os.remove(path)
            
        return jsonify({
            "message": f"Successfully processed {len(documents)} documents. You can now ask questions.",
            "caseDetails": extracted_details
        }), 200
    except Exception as e:
        logging.error(f"Upload processing failed: {e}", exc_info=True)
        return jsonify({"error": "An error occurred during document processing."}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """Receives a question and gets an answer from the RAG pipeline."""
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400
    if not rag_pipeline.qa_chain:
        return jsonify({"error": "Documents have not been processed yet."}), 400

    try:
        response = rag_pipeline.answer_question(question)
        session_manager.add_qa_pair(question, response)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Question answering failed: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while getting the answer."}), 500

@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    """Exports the current chat session to a PDF file."""
    data = request.get_json()
    case_details = {
        "name": data.get("caseName"),
        "number": data.get("caseNumber")
    }

    if not case_details["name"] or not case_details["number"]:
        return jsonify({"error": "Case Name and Case Number are required."}), 400

    try:
        pdf_buffer = BytesIO()
        exporter = PDFExporter(
            history=session_manager.get_history(),
            case_details=case_details,
            output_path=pdf_buffer
        )
        exporter.generate_pdf()
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"case_report_{case_details['name'].replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
    except ImportError:
         logging.error("PDF export failed because 'reportlab' is not installed.")
         return jsonify({"error": "PDF generation library (reportlab) not found on the server."}), 500
    except Exception as e:
        logging.error(f"PDF export failed: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during PDF export."}), 500

if __name__ == '__main__':
    print("Starting the AI Legal Assistant web server...")
    print("Open your browser and navigate to http://127.0.0.1:5000")
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)

