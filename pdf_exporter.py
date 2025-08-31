import os
from datetime import datetime
from typing import List, Dict, Any

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class PDFExporter:
    """Handles the creation of PDF reports from session history."""

    def __init__(self, history: List[Dict[str, Any]], case_details: Dict[str, str], output_path: str):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is not installed. Please run: pip install reportlab")
        
        self.history = history
        self.case_name = case_details.get("name", "N/A")
        self.case_number = case_details.get("number", "N/A")
        self.output_path = output_path
        self.location = "Sparks, Nevada, United States" # Placeholder location
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.styles = getSampleStyleSheet()
        self.story = []

    def _add_header(self):
        """Adds the case details header to the PDF."""
        header_style = self.styles['h1']
        header_text = f"Case Report: {self.case_name}"
        self.story.append(Paragraph(header_text, header_style))
        self.story.append(Spacer(1, 0.2 * inch))

        normal_style = self.styles['Normal']
        meta_info = [
            f"<b>Case Number:</b> {self.case_number}",
            f"<b>Date Generated:</b> {self.date}",
            f"<b>Location:</b> {self.location}"
        ]
        for line in meta_info:
            self.story.append(Paragraph(line, normal_style))
        
        self.story.append(Spacer(1, 0.4 * inch))

    def _add_qa_section(self):
        """Adds the question and answer pairs to the PDF."""
        title_style = self.styles['h2']
        self.story.append(Paragraph("Session History", title_style))
        self.story.append(Spacer(1, 0.2 * inch))
        
        question_style = self.styles['h4']
        answer_style = self.styles['BodyText']

        if not self.history:
            self.story.append(Paragraph("No questions were asked in this session.", answer_style))
            return

        for i, item in enumerate(self.history, 1):
            question_text = f"{i}. Question: {item.get('question', 'N/A')}"
            answer_text = f"Answer: {item.get('answer', {}).get('answer', 'N/A')}"
            
            self.story.append(Paragraph(question_text, question_style))
            self.story.append(Spacer(1, 0.1 * inch))
            self.story.append(Paragraph(answer_text, answer_style))
            self.story.append(Spacer(1, 0.3 * inch))

    def generate_pdf(self):
        """Builds and saves the final PDF document."""
        doc = SimpleDocTemplate(self.output_path, pagesize=letter)
        self._add_header()
        self._add_qa_section()
        doc.build(self.story)
