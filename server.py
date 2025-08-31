import os
import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

# --- FIX: Importing from original, corrected filenames ---
from file_handler import FileHandler
from rag_pipeline import RAGPipeline
from settings import Settings

# --- Basic Setup ---
app = Flask(__name__, template_folder='.') 
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set in .env file.")

UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Initialize Core Components ---
# WARNING: Using global variables makes the state shared across all users.
# This is okay for a simple demo but not for a production application.
try:
    file_handler = FileHandler()
    rag_pipeline = RAGPipeline(api_key=api_key)
except Exception as e:
    logging.error(f"FATAL: Could not initialize core components: {e}")
    rag_pipeline = None


# --- Web Routes ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    # Assuming you have an index.html file in the same directory
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handles file uploads from the user's computer."""
    global rag_pipeline
    if not rag_pipeline:
        return jsonify({"error": "Backend pipeline is not initialized."}), 500
        
    if 'files' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400

    saved_paths = []
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_paths.append(filepath)

    try:
        # Re-initialize the pipeline for a fresh state with the new documents.
        rag_pipeline = RAGPipeline(api_key=api_key)
        
        logging.info(f"Processing files: {saved_paths}")
        documents = file_handler.load_documents(saved_paths)
        if not documents:
            return jsonify({"error": "Could not extract text from the provided documents."}), 400
            
        rag_pipeline.build_vector_store(documents)
        
        return jsonify({
            "message": f"Successfully processed {len(documents)} document(s). Ready for questions.",
            "filenames": [doc['name'] for doc in documents]
        })

    except Exception as e:
        logging.error(f"Error during file processing: {e}", exc_info=True)
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500


@app.route('/ask', methods=['POST'])
def ask_question():
    """Handles questions from the user and returns the AI's answer."""
    if not rag_pipeline or not rag_pipeline.qa_chain:
        return jsonify({"error": "Knowledge base not ready. Please upload documents first."}), 400

    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({"error": "Question is missing"}), 400

    try:
        response = rag_pipeline.answer_question(question)
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error during question answering: {e}", exc_info=True)
        return jsonify({"error": f"An internal error occurred while getting an answer: {str(e)}"}), 500


if __name__ == '__main__':
    from waitress import serve
    print("Server starting at http://0.0.0.0:8080")
    serve(app, host="0.0.0.0", port=8080)
