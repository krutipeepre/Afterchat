import io
from fpdf import FPDF
from app.models import Conversation, Role

class ConversationPDF(FPDF):
    def header(self):
        """Renders a restrained editorial header on every page."""
        self.set_font("helvetica", "B", 10)
        self.set_text_color(161, 164, 158) # Muted gray
        self.cell(0, 10, "afterchat.", ln=True, align="R")
        
        # Subtle separator line
        self.set_draw_color(220, 220, 220)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def footer(self):
        """Renders page numbers at the bottom."""
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(161, 164, 158)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def generate_pdf(conversation: Conversation) -> io.BytesIO:
    """
    Generates a PDF byte stream from a Conversation object.
    Uses an in-memory buffer to avoid disk I/O.
    """
    pdf = ConversationPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title Section
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(13, 15, 14) # Deep black
    
    # FPDF's built-in Helvetica doesn't support full Unicode (like emojis). 
    # We safely encode/decode to latin-1 to replace unsupported chars with '?' and avoid crashes.
    safe_title = conversation.title.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=safe_title)
    
    # Meta Info (Source Platform)
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(112, 116, 109)
    pdf.cell(0, 10, txt=f"Source: {conversation.source}", ln=True)
    pdf.ln(8)
    
    # Messages Loop
    for msg in conversation.messages:
        # Determine speaker styling
        if msg.role == Role.USER:
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(41, 44, 40)
            speaker_name = "User"
        elif msg.role == Role.SYSTEM:
            pdf.set_font("helvetica", "I", 10)
            pdf.set_text_color(217, 83, 79) # Muted red for errors
            speaker_name = "System Note"
        else:
            pdf.set_font("helvetica", "B", 11)
            pdf.set_text_color(13, 15, 14)
            speaker_name = "AI Assistant"
            
        # Print Speaker Name
        pdf.cell(0, 8, txt=speaker_name, ln=True)
        
        # Print Message Content
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(21, 23, 21)
        
        # Clean text for PDF rendering
        safe_content = msg.content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, txt=safe_content)
        
        # Add spacing between messages
        pdf.ln(8)
        
    # Generate PDF bytes and wrap in a BytesIO buffer
    pdf_bytes = pdf.output()
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)
    
    return buffer