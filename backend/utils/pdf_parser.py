"""
PDF parsing utilities for resume extraction
"""

import re
from pathlib import Path
from typing import Optional, Dict
from PyPDF2 import PdfReader


def parse_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text content

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF is corrupted or unreadable

    Example:
        >>> text = parse_pdf("resume.pdf")
        >>> print(text[:100])
        "John Doe\nSoftware Engineer\n..."
    """
    pdf_file = Path(pdf_path)

    # Validate PDF path exists
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not pdf_file.is_file():
        raise ValueError(f"Path is not a file: {pdf_path}")

    try:
        # Open PDF with PyPDF2
        reader = PdfReader(str(pdf_file))

        # Extract text from all pages
        text_parts = []
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                # Log but continue with other pages
                print(f"Warning: Could not extract text from page {page_num + 1}: {e}")

        if not text_parts:
            raise ValueError("No text could be extracted from PDF")

        # Combine all pages
        full_text = "\n\n".join(text_parts)

        # Clean and normalize text
        return clean_resume_text(full_text)

    except Exception as e:
        raise ValueError(f"Error reading PDF file: {str(e)}")


def extract_sections(pdf_text: str) -> Dict[str, str]:
    """
    Attempt to identify resume sections (Education, Experience, Skills, etc.)

    Args:
        pdf_text: Full text from resume PDF

    Returns:
        Dict mapping section names to content

    Example:
        >>> sections = extract_sections(resume_text)
        >>> print(sections.keys())
        dict_keys(['education', 'experience', 'skills'])
    """
    # Common resume section headers (case-insensitive patterns)
    section_patterns = {
        "education": r"(?i)(education|academic background|degrees?)",
        "experience": r"(?i)(experience|work history|employment|professional experience)",
        "skills": r"(?i)(skills|technical skills|core competencies|expertise)",
        "projects": r"(?i)(projects|portfolio|selected projects)",
        "certifications": r"(?i)(certifications?|licenses?|credentials?)",
        "awards": r"(?i)(awards?|honors?|achievements?)",
        "summary": r"(?i)(summary|profile|objective|about)",
    }

    sections = {}
    lines = pdf_text.split("\n")

    current_section = "header"
    current_content = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line matches any section header
        section_found = None
        for section_name, pattern in section_patterns.items():
            if re.match(pattern, line):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                section_found = section_name
                current_section = section_name
                current_content = []
                break

        if not section_found:
            current_content.append(line)

    # Save last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def clean_resume_text(text: str) -> str:
    """
    Clean and normalize extracted PDF text

    Args:
        text: Raw text from PDF

    Returns:
        Cleaned text with normalized whitespace

    Processing:
        - Remove excessive whitespace
        - Normalize line breaks
        - Remove special characters that interfere with embedding
    """
    if not text:
        return ""

    # Normalize unicode characters
    text = text.encode("ascii", "ignore").decode("ascii")

    # Remove excessive whitespace
    text = re.sub(r" +", " ", text)

    # Normalize line breaks (remove single line breaks, keep double)
    text = re.sub(r"\n ", "\n", text)
    text = re.sub(r" \n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove common PDF artifacts
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]", "", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def validate_pdf(pdf_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate that a file is a readable PDF

    Args:
        pdf_path: Path to check

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> valid, error = validate_pdf("resume.pdf")
        >>> if not valid:
        ...     print(f"Invalid PDF: {error}")
    """
    pdf_file = Path(pdf_path)

    # Check file exists
    if not pdf_file.exists():
        return False, f"File does not exist: {pdf_path}"

    # Check is a file
    if not pdf_file.is_file():
        return False, f"Path is not a file: {pdf_path}"

    # Check file extension
    if pdf_file.suffix.lower() != ".pdf":
        return False, f"File does not have .pdf extension: {pdf_file.suffix}"

    # Check file is not empty
    if pdf_file.stat().st_size == 0:
        return False, "PDF file is empty"

    # Try to open with PyPDF2
    try:
        reader = PdfReader(str(pdf_file))

        # Check has pages
        if len(reader.pages) == 0:
            return False, "PDF has no pages"

        # Try to extract text from first page
        try:
            first_page_text = reader.pages[0].extract_text()
            if not first_page_text or len(first_page_text.strip()) == 0:
                return False, "PDF appears to contain no extractable text (might be image-based)"
        except Exception as e:
            return False, f"Cannot extract text from PDF: {str(e)}"

        return True, None

    except Exception as e:
        return False, f"Invalid or corrupted PDF: {str(e)}"


def get_pdf_metadata(pdf_path: str) -> Dict[str, any]:
    """
    Extract metadata from PDF file

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dict containing:
            - num_pages: Number of pages
            - file_size: File size in bytes
            - has_text: Whether PDF contains extractable text
            - estimated_words: Approximate word count

    Example:
        >>> meta = get_pdf_metadata("resume.pdf")
        >>> print(f"Pages: {meta['num_pages']}, Words: {meta['estimated_words']}")
    """
    pdf_file = Path(pdf_path)

    metadata = {
        "num_pages": 0,
        "file_size": 0,
        "has_text": False,
        "estimated_words": 0,
    }

    if not pdf_file.exists():
        return metadata

    metadata["file_size"] = pdf_file.stat().st_size

    try:
        reader = PdfReader(str(pdf_file))
        metadata["num_pages"] = len(reader.pages)

        # Try to extract text and count words
        full_text = []
        for page in reader.pages:
            try:
                text = page.extract_text()
                if text:
                    full_text.append(text)
            except:
                continue

        if full_text:
            metadata["has_text"] = True
            combined_text = " ".join(full_text)
            metadata["estimated_words"] = len(combined_text.split())

    except:
        pass

    return metadata
