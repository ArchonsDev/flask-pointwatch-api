import os
from datetime import datetime
from typing import Any, Callable, Iterable

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from werkzeug.datastructures import FileStorage
from sqlalchemy.orm import Query
import io

from ..models.proof import Proof
from ..models.user import User
from ..services.term_service import TermService

class PDFComposer:
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 20 * mm  # margin of 20mm
        self.y_position = self.page_height - self.margin
        self.buffer = io.BytesIO()  # Buffer to hold the PDF content in memory
        self.canvas = canvas.Canvas(self.buffer, pagesize=A4)
        self.line_height = 14  # Line height for text
        self.font_size = 12
        self.canvas.setFont("Helvetica", self.font_size)

    def add_text(self, text):
        """Add text to the PDF and handle pagination if necessary."""
        lines = text.split('\n')  # Handle multi-line text
        for line in lines:
            if self.y_position <= self.margin:  # Check if we need a new page
                self.add_new_page()
            self.canvas.drawString(self.margin, self.y_position, line)
            self.y_position -= self.line_height

    def add_new_page(self):
        """Handles adding a new page and resetting the y-position."""
        self.canvas.showPage()
        self.y_position = self.page_height - self.margin
        self.canvas.setFont("Helvetica", self.font_size)

    def add_paragraph(self, paragraph, max_width=None):
        """Add a paragraph that wraps text within the page width."""
        if max_width is None:
            max_width = self.page_width - 2 * self.margin

        # Split paragraph into words and handle word-wrapping
        words = paragraph.split(' ')
        line = ""
        for word in words:
            test_line = line + word + " "
            if self.canvas.stringWidth(test_line, "Helvetica", self.font_size) < max_width:
                line = test_line
            else:
                self.add_text(line.rstrip())
                line = word + " "
        self.add_text(line.rstrip())

    def draw_line(self):
        """Draws a horizontal line."""
        if self.y_position <= self.margin:
            self.add_new_page()
        self.canvas.setStrokeColor(colors.black)
        self.canvas.line(self.margin, self.y_position, self.page_width - self.margin, self.y_position)
        self.y_position -= self.line_height

    def get_pdf(self):
        """Finalize the PDF and return the buffer content."""
        self.canvas.save()  # Finalize the PDF
        self.buffer.seek(0)  # Move to the beginning of the buffer
        return self.buffer

class FTService:
    def __init__(self, db, term_service, clearing_service, user_service):
        self.data_dir = os.getenv('DATA_DIR', os.path.abspath('data'))
        self.db = db
        self.term_service = term_service
        self.clearing_service = clearing_service
        self.user_service = user_service

    def create_proof(self, **data: dict[str, Any]) -> Proof:
        proof = Proof(
            path=data.get("path"),
            filename=data.get("filename"),
            content_type=data.get("content_type"),
            swtd_form_id=data.get("swtd_form_id")
        )

        self.db.session.add(proof)
        self.db.session.commit()
        return proof

    def get_proof(self, filter_func: Callable[[Query, Proof], Iterable]) -> Proof:
        return filter_func(Proof.query, Proof)

    def save(self, user_id: int, swtd_id: int, file: FileStorage) -> Proof:
        user_fp = os.path.join(self.data_dir, str(user_id))

        if not os.path.exists(user_fp):
            os.mkdir(user_fp)

        user_swtd_fp = os.path.join(user_fp, str(swtd_id))

        if not os.path.exists(user_swtd_fp):
            os.mkdir(user_swtd_fp)

        proof = self.create_proof(
            path=os.path.join(user_swtd_fp, file.filename),
            filename=file.filename,
            content_type=file.content_type,
            swtd_form_id=swtd_id
        )

        user_swtd_proof_fp = os.path.join(user_swtd_fp, str(proof.id))

        if not os.path.exists(user_swtd_proof_fp):
            os.mkdir(user_swtd_proof_fp)

        fp = os.path.join(user_swtd_proof_fp, file.filename)

        proof = self.update_proof(proof, path=fp)

        file.save(fp)
        return proof

    def update_proof(self, proof: Proof, **data: dict[str, Any]) -> Proof:
        for key, value in data.items():
            if not hasattr(Proof, key):
                continue

            setattr(proof, key, value)

        self.db.session.commit()
        return proof

    def delete_proof(self, proof: Proof):
        try:
            os.remove(proof.path)  # Remove only the specific file
            self.db.session.delete(proof)  # Optionally, remove the proof entry from the database
            self.db.session.commit()  # Commit the changes to the database
        except FileNotFoundError:
            print(f"File {proof.path} not found.")
        except Exception as e:
            print(f"Error removing file: {e}")
        
    def export_for_employee(self, requester: User, user: User) -> io.BytesIO:
        pass

    def export_for_head(self, requester: User, user: User) -> io.BytesIO:
        pass

    def export_for_hr(self, requester: User, user: User) -> io.BytesIO:
        pass

# Sample usage
# def generate_pdf():
#     # Create the PDF using PDFComposer
#     pdf = PDFComposer()
#     pdf.add_text("This is a sample text to demonstrate PDF generation in memory.")
#     pdf.add_paragraph("Here is a longer paragraph that wraps automatically. The PDF will be generated dynamically and returned as a response.")
#     pdf.draw_line()
#     pdf.add_text("End of the PDF.")
    
#     # Get the in-memory PDF
#     pdf_buffer = pdf.get_pdf()

#     # Send the PDF as a response
#     response = make_response(send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='generated.pdf'))
#     response.headers['Content-Disposition'] = 'inline; filename=generated.pdf'
    
#     return response
