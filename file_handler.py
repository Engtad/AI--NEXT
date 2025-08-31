import os
import logging
from typing import List, Dict, Any, Optional
import requests
from urllib.parse import urlparse
from io import BytesIO
from tqdm import tqdm

# Conditional imports for PDF and DOCX processing
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

class FileHandler:
    """Handles loading and processing of documents from local paths and URLs."""

    def __init__(self):
        if not PYPDF_AVAILABLE:
            logging.warning("pypdf not installed. PDF processing is disabled. Run: pip install pypdf")
        if not DOCX_AVAILABLE:
            logging.warning("python-docx not installed. DOCX processing is disabled. Run: pip install python-docx")

    def _is_url(self, path: str) -> bool:
        """Checks if a given path is a well-formed URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _extract_text_from_stream(self, stream: BytesIO, content_type: str, url: str) -> Optional[str]:
        """Extracts text from a byte stream based on its content type."""
        try:
            if 'pdf' in content_type:
                if not PYPDF_AVAILABLE: return None
                reader = PdfReader(stream)
                return "".join(page.extract_text() for page in reader.pages if page.extract_text())
            elif 'openxmlformats-officedocument.wordprocessingml.document' in content_type:
                if not DOCX_AVAILABLE: return None
                document = docx.Document(stream)
                return "\n".join([para.text for para in document.paragraphs])
            elif 'text' in content_type:
                return stream.read().decode('utf-8')
            else:
                logging.warning(f"Unsupported content type '{content_type}' from URL: {url}")
                return None
        except Exception as e:
            logging.error(f"Failed to process content from stream for URL '{url}': {e}")
            return None

    def _load_from_url(self, url: str) -> Optional[str]:
        """Loads and processes a document from a URL by checking its content type."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'} # Some sites block requests without a user agent
            response = requests.get(url, timeout=30, headers=headers, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            content_stream = BytesIO(response.content)
            
            return self._extract_text_from_stream(content_stream, content_type, url)
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download file from URL '{url}': {e}")
            return None

    def _load_from_local(self, path: str) -> Optional[str]:
        """Loads a document from a local file path."""
        if not os.path.exists(path):
            logging.error(f"File not found at local path: '{path}'.")
            return None
        
        _, extension = os.path.splitext(path)
        
        try:
            if extension.lower() == '.pdf':
                if not PYPDF_AVAILABLE: return None
                with open(path, 'rb') as f:
                    return self._extract_text_from_stream(BytesIO(f.read()), 'application/pdf', path)
            
            elif extension.lower() == '.docx':
                if not DOCX_AVAILABLE: return None
                with open(path, 'rb') as f:
                    return self._extract_text_from_stream(BytesIO(f.read()), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', path)

            elif extension.lower() == '.txt':
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logging.warning(f"Unsupported local file type: '{extension}'.")
                return None
        except Exception as e:
            logging.error(f"Error reading file '{path}': {e}")
            return None

    def load_documents(self, sources: List[str]) -> List[Dict[str, Any]]:
        """Loads documents from a list of local paths or URLs."""
        loaded_docs = []
        if not sources:
            return loaded_docs

        for source in tqdm(sources, desc="Loading documents"):
            source = source.strip().strip('"\'')
            logging.info(f"Processing source: {source}")
            
            doc_content = None
            doc_name = "Unknown"

            if self._is_url(source):
                doc_content = self._load_from_url(source)
                doc_name = os.path.basename(urlparse(source).path) or "URL Document"
            else:
                doc_content = self._load_from_local(source)
                doc_name = os.path.basename(source)

            if doc_content and doc_content.strip():
                loaded_docs.append({'name': doc_name, 'content': doc_content})
            else:
                logging.warning(f"No content extracted from source: {source}")

        return loaded_docs
