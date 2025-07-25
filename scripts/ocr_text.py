import os
import fitz  # PyMuPDF
import ocrmypdf
import shutil
from pathlib import Path
import pymupdf4llm
from collections import Counter
import re
import pandas as pd

def is_scanned_pdf(pdf_path):
    """
    Returns True if the PDF likely lacks embedded text, False if born-digital/text-PDF.
    Returns None on error.
    """
    try:
        doc = fitz.open(pdf_path)
        # Consider all pages for robust detection
        pages_to_check = min(3, len(doc))
        for i in range(pages_to_check):
            text = doc[i].get_text().strip()
            if text:
                return False  # Found embedded text, so not scanned
        return True  # No text found in checked pages
    except Exception:
        return None


def normalize_heading_hierarchy(md_text):
    lines = md_text.split('\n')
    updated_lines = []
    for line in lines:
        match = re.match(r'^(#+)\s+(.*)', line)
        if match:
            hashes, content = match.groups()
            # Promote/demote based on content
            if len(hashes) == 1:
                hashes = '##'
            elif len(hashes) == 2:
                if any(word in content.lower() for word in ['mortality', 'knock-down', 'resistance', 'vector', 'prevalence']):
                    hashes = '###'
            line = f"{hashes} {content}"
        updated_lines.append(line)
    return '\n'.join(updated_lines)

def extract_markdown_with_hierarchy(pdf_path: Path, md_output_path: Path=None)->str:
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    
    # Set margins to exclude headers/footers (top: 50, bottom: 50 points)
    # This will ignore text in the top 50 points and bottom 50 points of each page
    default_margins = (0, 50, 0, 30)  # (left, top, right, bottom)
    
    if toc:
        # Use table of contents for header detection    
        toc_headers = pymupdf4llm.TocHeaders(doc)
        md_text = pymupdf4llm.to_markdown(
            doc, 
            hdr_info=toc_headers,
            margins=default_margins
        )
        print(f"📋 Used TocHeaders with {len(toc)} TOC entries and margins {default_margins}", end='\r')
    else:
        # Generate header info with custom settings when no TOC exists
        my_headers = pymupdf4llm.IdentifyHeaders(
            doc, 
            max_levels=3,  # Limit to 3 header levels
            body_limit=11  # Font size limit for body text
        )
        md_text = pymupdf4llm.to_markdown(
            doc, 
            hdr_info=my_headers,
            margins=default_margins
        )
        print("🔍 Used IdentifyHeaders with custom settings and margins", end='\r')
    
    if md_output_path:
        with open(md_output_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        
        print(f"✅ Markdown with hierarchy and margins saved: {md_output_path}", end='\r')
        
    return md_text

def process_pdf_pipeline(pdf_path: Path, output_dir = Path("temp_ocr"), temp_dir = Path("temp_ocr")) -> str:
    filename = Path(pdf_path).stem
    
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(exist_ok=True)

    ocr_path = temp_dir / f"{filename}_ocr.pdf"
    md_output = output_dir / f"{filename}.md"

    print(f"🔍 Processing PDF: {pdf_path}", end='\r')
    scanned = is_scanned_pdf(pdf_path)

    if scanned:
        print("🧾 Detected scanned PDF", end='\r')
        run_ocr(pdf_path, ocr_path)
        used_pdf = ocr_path
    else:
        print("📄 Detected born-digital PDF", end='\r')
        used_pdf = Path(pdf_path)

    return extract_markdown_with_hierarchy(used_pdf, md_output)

def run_ocr(input_path: Path, output_path: Path):
    print("🔁 Running OCRmyPDF...", end='\r')
    ocrmypdf.ocr(
        input_file=input_path,
        output_file=output_path,
        rotate_pages=True,
        deskew=True,
        force_ocr=True,
        skip_text=True
    )
    print(f"✅ OCR complete: {output_path}", end='\r')

def analyze_markdown_header_hierarchy(md_text: str) -> dict:
    """
    Extracts all header lines from markdown, assesses header hierarchy quality,
    and returns a pandas DataFrame with histogram counts of each header level.
    """
    # Extract header lines
    header_lines = [line for line in md_text.split('\n') if re.match(r'^#+\s', line)]
    
    # Count header levels
    header_levels = [len(re.match(r'^(#+)', line).group(1)) for line in header_lines]
    level_counts = Counter(header_levels)
    
    # Create DataFrame
    # Build the header level counts as a sorted list of tuples
    header_counts = sorted(level_counts.items())

    # Assess quality (simple heuristics)
    assessment = []
    if not header_levels:
        assessment.append('No headers found.')
    else:
        if 1 not in header_levels:
            assessment.append('No top-level (#) header found.')
        if min(header_levels) > 1:
            assessment.append('Headers do not start at top level.')
        if max(header_levels) - min(header_levels) > 2:
            assessment.append('Header levels are too deeply nested.')
        if len(set(header_levels)) == 1:
            assessment.append('Only one header level used.')
        if not assessment:
            assessment.append('Header hierarchy appears reasonable.')

    # Return as a dict
    return {
        **{f"hdr_level_{level}": count for level, count in header_counts},
        "assessment": ' '.join(assessment),
    }