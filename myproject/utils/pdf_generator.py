from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import FileResponse, HttpResponse
from reportlab.lib.pagesizes import letter
import re

def clean_text(text):
    # Remove non-printable or problematic characters
    return re.sub(r'[^\x09\x0A\x0D\x20-\x7E]', '', text)

def generate_pdf_response(content, filename="notes.pdf"):
    try:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        text = p.beginText(40, 750)
        text.setFont("Helvetica", 12)

        # Clean and split content
        cleaned_content = clean_text(content)
        lines = cleaned_content.split('\n')

        for line in lines:
            if text.getY() < 40:  # If close to bottom, start new page
                p.drawText(text)
                p.showPage()
                text = p.beginText(40, 750)
                text.setFont("Helvetica", 12)
            text.textLine(line.strip())

        p.drawText(text)
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=filename)

    except Exception as e:
        return HttpResponse(f"PDF generation failed: {str(e)}", status=500)
