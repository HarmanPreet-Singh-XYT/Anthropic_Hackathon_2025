
from reportlab.pdfgen import canvas
import os

def create_pdf(path):
    c = canvas.Canvas(path)
    c.drawString(100, 750, "John Doe")
    c.drawString(100, 730, "Education: University of Testing")
    c.drawString(100, 710, "Experience: Community Leader")
    c.drawString(100, 690, "I have demonstrated strong leadership in my community service projects.")
    c.drawString(100, 670, "Founded a non-profit for coding education.")
    c.drawString(100, 650, "Academic Excellence: 4.0 GPA")
    c.save()

if __name__ == "__main__":
    os.makedirs("backend/data", exist_ok=True)
    create_pdf("backend/data/sample_resume.pdf")
    print("Created backend/data/sample_resume.pdf")
