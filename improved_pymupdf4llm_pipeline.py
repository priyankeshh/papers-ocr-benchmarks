# %% [markdown]
# # Improved PDF Processing Pipeline with Better Formatting and Metadata
# 
# This enhanced version focuses on:
# 1. **Better Markdown formatting** with proper hierarchy (#, ##, ###)
# 2. **Enhanced metadata extraction** (title, authors, date, journal, etc.)
# 3. **Structured content organization** with proper sections
# 4. **Academic paper-specific parsing** for scientific literature

# %%
import os
import sys
import subprocess
import tempfile
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
from datetime import datetime

# Core PDF processing libraries
import fitz  # PyMuPDF
import pymupdf4llm
import ocrmypdf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# %% [markdown]
# ## Enhanced Metadata Extraction Functions

# %%
def extract_enhanced_metadata(pdf_path: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from PDF including academic paper information.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary containing enhanced metadata
    """
    metadata = {
        "title": None,
        "authors": [],
        "journal": None,
        "date_published": None,
        "doi": None,
        "abstract": None,
        "keywords": [],
        "page_count": 0,
        "language": "en",
        "subject": None,
        "creation_date": None,
        "modification_date": None,
        "creator": None,
        "producer": None
    }
    
    try:
        doc = fitz.open(pdf_path)
        
        # Extract basic PDF metadata
        pdf_metadata = doc.metadata
        metadata["page_count"] = len(doc)
        
        if pdf_metadata:
            metadata["title"] = pdf_metadata.get("title", "").strip()
            metadata["subject"] = pdf_metadata.get("subject", "").strip()
            metadata["creation_date"] = pdf_metadata.get("creationDate", "")
            metadata["modification_date"] = pdf_metadata.get("modDate", "")
            metadata["creator"] = pdf_metadata.get("creator", "")
            metadata["producer"] = pdf_metadata.get("producer", "")
            
            # Extract keywords from metadata
            keywords_str = pdf_metadata.get("keywords", "")
            if keywords_str:
                metadata["keywords"] = [kw.strip() for kw in keywords_str.split(",") if kw.strip()]
        
        # Extract text from first few pages for content analysis
        first_page_text = ""
        for page_num in range(min(3, len(doc))):
            page = doc[page_num]
            first_page_text += page.get_text() + "\n"
        
        # Enhanced content-based metadata extraction
        metadata.update(extract_academic_metadata(first_page_text))
        
        doc.close()
        
        # Clean up extracted data
        metadata = clean_metadata(metadata)
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}")
        return metadata

# %%
def extract_academic_metadata(text: str) -> Dict[str, Any]:
    """
    Extract academic paper-specific metadata from text content.
    
    Args:
        text: Text content from PDF
        
    Returns:
        Dictionary containing academic metadata
    """
    metadata = {
        "title": None,
        "authors": [],
        "journal": None,
        "date_published": None,
        "doi": None,
        "abstract": None,
        "keywords": []
    }
    
    # Extract DOI
    doi_pattern = r'(?:DOI|doi)[\s:]*([0-9]{2}\.[0-9]{4}\/[^\s]+)'
    doi_match = re.search(doi_pattern, text, re.IGNORECASE)
    if doi_match:
        metadata["doi"] = doi_match.group(1)
    
    # Extract title (usually the largest text on first page)
    title_patterns = [
        r'^([A-Z][^.!?]*(?:[.!?][A-Z][^.!?]*)*)\n',  # Title at start
        r'\n([A-Z][^.!?]*(?:[.!?][A-Z][^.!?]*)*)\n(?=\n|[A-Z])',  # Title with newlines
        r'(?:Title|TITLE)[\s:]*([^\n]+)',  # Explicit title
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            potential_title = match.group(1).strip()
            if 10 < len(potential_title) < 200:  # Reasonable title length
                metadata["title"] = potential_title
                break
    
    # Extract authors
    author_patterns = [
        r'(?:Authors?|BY)[\s:]*([^\n]+)',
        r'([A-Z][a-z]+ [A-Z][a-z]+(?:,\s*[A-Z][a-z]+ [A-Z][a-z]+)*)',
        r'([A-Z]\.\s*[A-Z][a-z]+(?:,\s*[A-Z]\.\s*[A-Z][a-z]+)*)',
    ]
    
    for pattern in author_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        if matches:
            for author_string in matches:
                authors = [author.strip() for author in author_string.split(',')]
                metadata["authors"].extend(authors)
            break
    
    # Extract journal information
    journal_patterns = [
        r'(?:Journal|Proceedings|Conference)[\s:]*([^\n]+)',
        r'Published in[\s:]*([^\n]+)',
        r'([A-Z][a-z]+ Journal[^\n]*)',
    ]
    
    for pattern in journal_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["journal"] = match.group(1).strip()
            break
    
    # Extract publication date
    date_patterns = [
        r'(?:Published|Publication date|Date)[\s:]*([0-9]{4})',
        r'([0-9]{1,2}[\s/-][0-9]{1,2}[\s/-][0-9]{4})',
        r'([A-Z][a-z]+ [0-9]{1,2}, [0-9]{4})',
        r'([0-9]{4})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["date_published"] = match.group(1)
            break
    
    # Extract abstract
    abstract_pattern = r'(?:Abstract|ABSTRACT)[\s:]*\n?(.*?)(?=\n\n|Keywords|Introduction|1\.|\n[A-Z])'
    abstract_match = re.search(abstract_pattern, text, re.DOTALL | re.IGNORECASE)
    if abstract_match:
        abstract_text = abstract_match.group(1).strip()
        if len(abstract_text) > 50:  # Reasonable abstract length
            metadata["abstract"] = abstract_text
    
    # Extract keywords
    keywords_pattern = r'(?:Keywords?|Key words?)[\s:]*([^\n]+)'
    keywords_match = re.search(keywords_pattern, text, re.IGNORECASE)
    if keywords_match:
        keywords_str = keywords_match.group(1)
        keywords = [kw.strip() for kw in re.split(r'[,;]', keywords_str) if kw.strip()]
        metadata["keywords"] = keywords
    
    return metadata

# %%
def clean_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and normalize extracted metadata.
    
    Args:
        metadata: Raw metadata dictionary
        
    Returns:
        Cleaned metadata dictionary
    """
    # Clean title
    if metadata.get("title"):
        title = metadata["title"]
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        # Remove common artifacts
        title = re.sub(r'^(Title|TITLE)[\s:]*', '', title)
        metadata["title"] = title
    
    # Clean authors
    if metadata.get("authors"):
        cleaned_authors = []
        for author in metadata["authors"]:
            author = author.strip()
            if author and len(author) > 2:
                # Remove common artifacts
                author = re.sub(r'[0-9*,]+$', '', author).strip()
                if author:
                    cleaned_authors.append(author)
        metadata["authors"] = cleaned_authors[:10]  # Limit to reasonable number
    
    # Clean journal
    if metadata.get("journal"):
        journal = metadata["journal"]
        journal = re.sub(r'\s+', ' ', journal).strip()
        metadata["journal"] = journal
    
    # Clean keywords
    if metadata.get("keywords"):
        cleaned_keywords = []
        for keyword in metadata["keywords"]:
            keyword = keyword.strip()
            if keyword and len(keyword) > 1:
                cleaned_keywords.append(keyword)
        metadata["keywords"] = cleaned_keywords[:20]  # Limit to reasonable number
    
    return metadata

# %% [markdown]
# ## Enhanced Content Formatting Functions

# %%
def format_enhanced_markdown(extracted_content: Any, metadata: Dict[str, Any]) -> str:
    """
    Format extracted content into properly structured markdown with hierarchy.
    
    Args:
        extracted_content: Raw content from PyMuPDF4LLM
        metadata: Enhanced metadata
        
    Returns:
        Formatted markdown string
    """
    markdown_parts = []
    
    # Add title
    if metadata.get("title"):
        markdown_parts.append(f"# {metadata['title']}\n")
    
    # Add metadata section
    metadata_section = format_metadata_section(metadata)
    if metadata_section:
        markdown_parts.append(metadata_section)
    
    # Process and format main content
    content_str = str(extracted_content) if extracted_content else ""
    
    # Clean up the content
    content_str = clean_content_text(content_str)
    
    # Structure the content with proper headers
    structured_content = structure_content_with_headers(content_str)
    
    markdown_parts.append(structured_content)
    
    return "\n".join(markdown_parts)

# %%
def format_metadata_section(metadata: Dict[str, Any]) -> str:
    """
    Format metadata into a structured markdown section.
    
    Args:
        metadata: Metadata dictionary
        
    Returns:
        Formatted metadata section
    """
    sections = []
    
    # Authors
    if metadata.get("authors"):
        authors_str = ", ".join(metadata["authors"])
        sections.append(f"**Authors:** {authors_str}")
    
    # Journal
    if metadata.get("journal"):
        sections.append(f"**Journal:** {metadata['journal']}")
    
    # Publication date
    if metadata.get("date_published"):
        sections.append(f"**Published:** {metadata['date_published']}")
    
    # DOI
    if metadata.get("doi"):
        sections.append(f"**DOI:** {metadata['doi']}")
    
    # Keywords
    if metadata.get("keywords"):
        keywords_str = ", ".join(metadata["keywords"])
        sections.append(f"**Keywords:** {keywords_str}")
    
    # Page count
    if metadata.get("page_count"):
        sections.append(f"**Pages:** {metadata['page_count']}")
    
    if sections:
        return "## Document Information\n\n" + "\n\n".join(sections) + "\n\n---\n\n"
    
    return ""

# %%
def clean_content_text(content: str) -> str:
    """
    Clean and normalize content text.
    
    Args:
        content: Raw content string
        
    Returns:
        Cleaned content string
    """
    # Remove metadata dictionary if present
    if content.startswith("{'metadata'"):
        # Find the end of the metadata dictionary
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for i, char in enumerate(content):
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
            
            if not in_string:
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        content = content[i+1:].strip()
                        break
    
    # Clean up excessive whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    content = re.sub(r' +', ' ', content)
    
    # Remove page numbers and headers/footers
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip obvious page numbers
        if re.match(r'^\d+$', line):
            continue
        # Skip short lines that are likely headers/footers
        if len(line) < 5:
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

# %%
def structure_content_with_headers(content: str) -> str:
    """
    Add proper markdown headers to structure the content.
    
    Args:
        content: Cleaned content string
        
    Returns:
        Content with proper markdown headers
    """
    lines = content.split('\n')
    structured_lines = []
    
    # Common section headers in academic papers
    section_patterns = [
        (r'^(Abstract|ABSTRACT)$', '## Abstract'),
        (r'^(Introduction|INTRODUCTION)$', '## Introduction'),
        (r'^(Background|BACKGROUND)$', '## Background'),
        (r'^(Methods?|METHODS?)$', '## Methods'),
        (r'^(Results?|RESULTS?)$', '## Results'),
        (r'^(Discussion|DISCUSSION)$', '## Discussion'),
        (r'^(Conclusion|CONCLUSION|Conclusions|CONCLUSIONS)$', '## Conclusion'),
        (r'^(References?|REFERENCES?)$', '## References'),
        (r'^(Acknowledgments?|ACKNOWLEDGMENTS?)$', '## Acknowledgments'),
        (r'^(Appendix|APPENDIX)$', '## Appendix'),
        (r'^(\d+\.\s*[A-Z][^.]*?)$', '## \\1'),  # Numbered sections
        (r'^([A-Z][A-Z\s]{3,}[A-Z])$', '## \\1'),  # ALL CAPS headers
    ]
    
    subsection_patterns = [
        (r'^(\d+\.\d+\s*[A-Z][^.]*?)$', '### \\1'),  # Numbered subsections
        (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):$', '### \\1'),  # Title case with colon
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            structured_lines.append('')
            continue
        
        # Check for main section headers
        header_found = False
        for pattern, replacement in section_patterns:
            if re.match(pattern, line):
                structured_lines.append(f'\n{replacement}\n')
                header_found = True
                break
        
        if not header_found:
            # Check for subsection headers
            for pattern, replacement in subsection_patterns:
                if re.match(pattern, line):
                    structured_lines.append(f'\n{replacement}\n')
                    header_found = True
                    break
        
        if not header_found:
            # Check if line looks like a header (bold, larger font, etc.)
            if is_likely_header(line):
                level = determine_header_level(line)
                header_prefix = '#' * level
                structured_lines.append(f'\n{header_prefix} {line}\n')
            else:
                structured_lines.append(line)
    
    return '\n'.join(structured_lines)

# %%
def is_likely_header(line: str) -> bool:
    """
    Determine if a line is likely a header based on various criteria.
    
    Args:
        line: Text line to analyze
        
    Returns:
        True if line is likely a header
    """
    # Check for bold formatting
    if line.startswith('**') and line.endswith('**'):
        return True
    
    # Check for title case
    if line.istitle() and len(line.split()) <= 8:
        return True
    
    # Check for all caps (but not too long)
    if line.isupper() and 5 <= len(line) <= 50:
        return True
    
    # Check for numbered headers
    if re.match(r'^\d+\.?\s+[A-Z]', line):
        return True
    
    # Check for common header patterns
    header_indicators = [
        'Background:', 'Methods:', 'Results:', 'Discussion:', 'Conclusion:',
        'Introduction:', 'Abstract:', 'References:', 'Acknowledgments:'
    ]
    
    for indicator in header_indicators:
        if line.startswith(indicator):
            return True
    
    return False

# %%
def determine_header_level(line: str) -> int:
    """
    Determine the appropriate header level for a line.
    
    Args:
        line: Header line text
        
    Returns:
        Header level (2-4)
    """
    # Main section headers
    main_sections = [
        'abstract', 'introduction', 'background', 'methods', 'results',
        'discussion', 'conclusion', 'references', 'acknowledgments'
    ]
    
    if any(section in line.lower() for section in main_sections):
        return 2
    
    # Numbered sections
    if re.match(r'^\d+\.?\s+', line):
        return 2
    
    # Numbered subsections
    if re.match(r'^\d+\.\d+', line):
        return 3
    
    # Default to level 3 for other headers
    return 3

# %% [markdown]
# ## Enhanced Main Processing Pipeline

# %%
def process_pdf_enhanced(input_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Enhanced PDF processing pipeline with better formatting and metadata.
    
    Args:
        input_path: Path to input PDF file
        output_dir: Directory for output files (optional)
        
    Returns:
        Dictionary containing processing results and metadata
    """
    start_time = time.time()
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"PDF file not found: {input_path}")
    
    # Setup output directory
    if output_dir is None:
        output_dir = Path(input_path).parent / "enhanced_processed"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize results dictionary
    results = {
        "input_path": input_path,
        "output_dir": output_dir,
        "processing_start": start_time,
        "pdf_type": None,
        "has_toc": False,
        "ocr_applied": False,
        "processed_pdf_path": None,
        "extraction_method": None,
        "enhanced_metadata": {},
        "formatted_content": None,
        "output_files": {},
        "processing_time": None,
        "errors": []
    }
    
    try:
        logger.info(f"Starting enhanced PDF processing: {input_path}")
        
        # Step 1: Extract enhanced metadata
        logger.info("Step 1: Extracting enhanced metadata...")
        enhanced_metadata = extract_enhanced_metadata(input_path)
        results["enhanced_metadata"] = enhanced_metadata
        
        # Step 2: Analyze PDF type
        logger.info("Step 2: Analyzing PDF type...")
        is_scanned = is_pdf_scanned(input_path)
        has_toc = has_table_of_contents(input_path)
        
        results["pdf_type"] = "scanned" if is_scanned else "born_digital"
        results["has_toc"] = has_toc
        
        # Step 3: Preprocess if needed
        processed_pdf_path = input_path
        
        if is_scanned:
            logger.info("Step 3: Applying OCRmyPDF preprocessing...")
            base_name = Path(input_path).stem
            ocr_output_path = os.path.join(output_dir, f"{base_name}_ocr_processed.pdf")
            processed_pdf_path = preprocess_with_ocrmypdf(input_path, ocr_output_path)
            results["ocr_applied"] = True
            results["processed_pdf_path"] = processed_pdf_path
            
            # Re-check TOC after OCR
            has_toc = has_table_of_contents(processed_pdf_path)
            results["has_toc"] = has_toc
        
        # Step 4: Extract content with PyMuPDF4LLM
        logger.info("Step 4: Extracting content with PyMuPDF4LLM...")
        extraction_start = time.time()
        
        # Configure PyMuPDF4LLM parameters
        pymupdf_params = {
            "page_chunks": True,
            "write_images": True,
            "image_path": os.path.join(output_dir, "images"),
            "image_format": "png",
            "extract_words": True
        }
        
        # Extract content
        extracted_content = pymupdf4llm.to_markdown(
            processed_pdf_path,
            **pymupdf_params
        )
        
        extraction_time = time.time() - extraction_start
        results["extraction_method"] = "enhanced_pymupdf4llm"
        
        # Step 5: Format content with enhanced structure
        logger.info("Step 5: Formatting content with enhanced structure...")
        formatted_content = format_enhanced_markdown(extracted_content, enhanced_metadata)
        results["formatted_content"] = formatted_content
        
        # Step 6: Save all outputs
        logger.info("Step 6: Saving enhanced outputs...")
        base_name = Path(input_path).stem
        
        # Save enhanced markdown
        markdown_path = os.path.join(output_dir, f"{base_name}_enhanced.md")
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        # Save enhanced metadata
        metadata_path = os.path.join(output_dir, f"{base_name}_enhanced_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_metadata, f, indent=2, default=str)
        
        # Save processing report
        report_path = os.path.join(output_dir, f"{base_name}_processing_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            report = {k: v for k, v in results.items() if k != 'formatted_content'}
            json.dump(report, f, indent=2, default=str)
        
        results["output_files"] = {
            "markdown": markdown_path,
            "metadata": metadata_path,
            "report": report_path
        }
        
        # Calculate total processing time
        total_time = time.time() - start_time
        results["processing_time"] = total_time
        
        logger.info(f"Enhanced processing completed successfully in {total_time:.2f} seconds")
        
        return results
        
    except Exception as e:
        error_msg = f"Enhanced processing failed: {str(e)}"
        logger.error(error_msg)
        results["errors"].append(error_msg)
        results["processing_time"] = time.time() - start_time
        return results

# %% [markdown]
# ## Utility Functions (from original pipeline)

# %%
def is_pdf_scanned(pdf_path: str, text_threshold: float = 0.1) -> bool:
    """
    Detect if a PDF is scanned (image-based) or born-digital.
    """
    try:
        doc = fitz.open(pdf_path)
        total_chars = 0
        total_area = 0
        
        sample_pages = min(5, len(doc))
        
        for page_num in range(sample_pages):
            page = doc[page_num]
            text = page.get_text()
            total_chars += len(text.strip())
            total_area += page.rect.width * page.rect.height
        
        doc.close()
        
        if total_area == 0:
            return True
            
        text_density = total_chars / total_area
        is_scanned = text_density < text_threshold
        
        logger.info(f"PDF analysis: {total_chars} chars, density: {text_density:.6f}, scanned: {is_scanned}")
        return is_scanned
        
    except Exception as e:
        logger.error(f"Error analyzing PDF: {e}")
        return True

# %%
def has_table_of_contents(pdf_path: str) -> bool:
    """
    Check if PDF has an embedded table of contents.
    """
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        doc.close()
        return len(toc) > 0
    except Exception as e:
        logger.error(f"Error checking TOC: {e}")
        return False

# %%
def preprocess_with_ocrmypdf(input_path: str, output_path: str = None) -> str:
    """
    Preprocess PDF with OCRmyPDF to add OCR layer and fix orientation.
    """
    if output_path is None:
        temp_dir = tempfile.gettempdir()
        base_name = Path(input_path).stem
        output_path = os.path.join(temp_dir, f"{base_name}_ocr_processed.pdf")
    
    try:
        logger.info(f"Starting OCRmyPDF preprocessing: {input_path}")
        start_time = time.time()
        
        ocrmypdf.ocr(
            input_path,
            output_path,
            language=['eng'],
            rotate_pages=True,
            deskew=True,
            clean=True,
            optimize=1,
            pdf_renderer='hocr',
            force_ocr=False,
            skip_text=False,
            redo_ocr=False,
            progress_bar=False,
            quiet=True
        )
        
        processing_time = time.time() - start_time
        logger.info(f"OCRmyPDF completed in {processing_time:.2f} seconds")
        
        return output_path
        
    except Exception as e:
        logger.error(f"OCRmyPDF preprocessing failed: {e}")
        return input_path

# %% [markdown]
# ## Example Usage

# %%
def main():
    """
    Example usage of the enhanced PDF processing pipeline.
    """
    # Example: Process a single PDF with enhanced features
    pdf_path = r"d:\extralit-benchmark\papers-ocr-benchmarks\pdfs\Allossogbe_et_al_2017_Mal_J.pdf"
    
    if os.path.exists(pdf_path):
        try:
            print("=== Enhanced PDF Processing ===")
            results = process_pdf_enhanced(pdf_path)
            
            print(f"\n✅ Processing completed!")
            print(f"📄 PDF Type: {results['pdf_type']}")
            print(f"📚 Has TOC: {results['has_toc']}")
            print(f"🔍 OCR Applied: {results['ocr_applied']}")
            print(f"⏱️ Processing Time: {results['processing_time']:.2f} seconds")
            
            # Display enhanced metadata
            metadata = results['enhanced_metadata']
            print(f"\n📋 Enhanced Metadata:")
            print(f"  • Title: {metadata.get('title', 'N/A')}")
            print(f"  • Authors: {', '.join(metadata.get('authors', []))}")
            print(f"  • Journal: {metadata.get('journal', 'N/A')}")
            print(f"  • Date: {metadata.get('date_published', 'N/A')}")
            print(f"  • DOI: {metadata.get('doi', 'N/A')}")
            print(f"  • Keywords: {', '.join(metadata.get('keywords', []))}")
            
            # Display output files
            print(f"\n📁 Output Files:")
            for file_type, path in results['output_files'].items():
                print(f"  • {file_type.capitalize()}: {path}")
            
            if results['errors']:
                print(f"\n❌ Errors: {results['errors']}")
            
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
    else:
        print(f"❌ PDF file not found: {pdf_path}")

# %%
if __name__ == "__main__":
    main()

print("\n🚀 Enhanced PDF Processing Pipeline Ready!")
print("Key improvements:")
print("  • 📝 Better markdown formatting with proper headers")
print("  • 📊 Enhanced metadata extraction (title, authors, journal, etc.)")
print("  • 🎯 Academic paper-specific parsing")
print("  • 📚 Structured content organization")
print("  • 🔧 Improved text cleaning and formatting")
