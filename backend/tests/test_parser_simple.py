
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from utils.pdf_parser import extract_sections

sample_resume = """
John Doe
Software Engineer

Education
University of Tech, BS Computer Science, 2020

Experience
Software Engineer, Tech Corp
- Built things
- Fixed bugs

Skills
Python, JavaScript
"""

sections = extract_sections(sample_resume)
print(sections)
