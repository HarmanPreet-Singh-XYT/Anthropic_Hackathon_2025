
from reportlab.pdfgen import canvas
import os
from pathlib import Path

def create_pdf(path):
    c = canvas.Canvas(str(path))
    c.drawString(100, 750, "John Doe")
    c.drawString(100, 730, "Education: University of Testing")
    c.drawString(100, 710, "Experience: Community Leader")
    c.drawString(100, 690, "I have demonstrated strong leadership in my community service projects.")
    c.drawString(100, 670, "Founded a non-profit for coding education.")
    c.drawString(100, 650, "Academic Excellence: 4.0 GPA")
    c.save()

if __name__ == "__main__":
    # Calculate paths relative to this script
    # script is in backend/scripts/
    # data should be in backend/data/
    root_dir = Path(__file__).parent.parent.parent
    data_dir = root_dir / "backend" / "data"
    
    os.makedirs(data_dir, exist_ok=True)
    
    output_path = data_dir / "sample_resume.pdf"
    create_pdf(output_path)
    print(f"Created {output_path}")
