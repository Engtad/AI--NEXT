import logging
from typing import List, Dict, Any

# --- FIX: Importing from original, corrected filename ---
from settings import Settings

# LangChain components for Anthropic and HuggingFace
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

class RAGPipeline:
    """Manages the core RAG logic (embedding, vector store, QA chain)."""

    def __init__(self, api_key: str):
        self.vector_store = None
        self.qa_chain = None

        try:
            # 1. Initialize local, open-source model for embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=Settings.get('llm.embedding_model')
            )

            # 2. Initialize Anthropic's model for generation
            self.llm = ChatAnthropic(
                model=Settings.get('llm.generation_model'),
                temperature=0.1, # Set temperature to 0.1 as requested previously
                anthropic_api_key=api_key
            )
        except Exception as e:
            logging.error(f"Failed to initialize AI models: {e}")
            raise ValueError("Could not initialize AI models. Check your API key and model names in config.yaml.")

    def build_vector_store(self, documents: List[Dict[str, Any]]):
        """Builds the FAISS vector store from processed documents."""
        logging.info("Building vector store...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Settings.get('chunking.chunk_size', 1500),
            chunk_overlap=Settings.get('chunking.chunk_overlap', 200)
        )
        
        all_chunks = []
        for doc in documents:
            texts = text_splitter.split_text(doc['content'])
            for i, text_chunk in enumerate(texts):
                metadata = {"source": doc.get('name', 'Unknown'), "chunk_id": i}
                all_chunks.append({"text": text_chunk, "metadata": metadata})

        chunk_texts = [chunk['text'] for chunk in all_chunks]
        chunk_metadatas = [chunk['metadata'] for chunk in all_chunks]
        
        if not chunk_texts:
            logging.warning("No text chunks were generated from the documents.")
            self.vector_store = None
            return

        try:
            self.vector_store = FAISS.from_texts(
                texts=chunk_texts, 
                embedding=self.embeddings,
                metadatas=chunk_metadatas
            )
            logging.info("Vector store built successfully.")
            self._create_qa_chain()
        except Exception as e:
            logging.error(f"Failed to build FAISS vector store: {e}")
            self.vector_store = None

    def _create_qa_chain(self):
        """Creates the question-answering chain."""
        if not self.vector_store:
            logging.error("Cannot create QA chain without a vector store.")
            return

        search_kwargs = {"k": Settings.get('retrieval.k_results', 5)}
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type=Settings.get('retrieval.search_type', "similarity"),
                search_kwargs=search_kwargs
            ),
            return_source_documents=True
        )
        logging.info("QA chain created successfully.")

    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answers a question using the RAG pipeline."""
        if not self.qa_chain:
            return {"answer": "The knowledge base is not ready. Please load documents first.", "sources": []}

        logging.info(f"Answering question: {question}")
        response = self.qa_chain.invoke({"query": question})
        
        sources = [
            {
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_id": doc.metadata.get("chunk_id", -1)
            } for doc in response.get("source_documents", [])
        ]
        
        return {
            "answer": response.get("result", "No answer found."),
            "sources": sources
        }
