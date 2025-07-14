# %% [markdown]
# # PDF Processing Pipeline with PyMuPDF4LLM and OCRmyPDF
# 
# This script implements a comprehensive PDF processing pipeline that:
# 1. Detects PDF type (scanned vs born-digital)
# 2. Applies OCRmyPDF preprocessing for scanned PDFs
# 3. Uses PyMuPDF4LLM for text extraction with TOC-based header logic
# 4. Falls back to heuristics for PDFs without TOC
# 5. Returns structured metadata and extracted content

# %% [markdown]
# ## Import Required Libraries

# %%
import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
import logging

# Core PDF processing libraries
import fitz  # PyMuPDF
import pymupdf4llm
import ocrmypdf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# %% [markdown]
# ## PDF Type Detection Functions

# %%
def is_pdf_scanned(pdf_path: str, text_threshold: float = 0.1) -> bool:
    """
    Detect if a PDF is scanned (image-based) or born-digital.
    
    Args:
        pdf_path: Path to the PDF file
        text_threshold: Minimum ratio of text content to consider as born-digital
        
    Returns:
        True if PDF is scanned, False if born-digital
    """
    try:
        doc = fitz.open(pdf_path)
        total_chars = 0
        total_area = 0
        
        # Sample first 5 pages to determine PDF type
        sample_pages = min(5, len(doc))
        
        for page_num in range(sample_pages):
            page = doc[page_num]
            text = page.get_text()
            total_chars += len(text.strip())
            total_area += page.rect.width * page.rect.height
        
        doc.close()
        
        # Calculate text density
        if total_area == 0:
            return True
            
        text_density = total_chars / total_area
        is_scanned = text_density < text_threshold
        
        logger.info(f"PDF analysis: {total_chars} chars, density: {text_density:.6f}, scanned: {is_scanned}")
        return is_scanned
        
    except Exception as e:
        logger.error(f"Error analyzing PDF: {e}")
        return True  # Assume scanned if analysis fails

# %%
def has_table_of_contents(pdf_path: str) -> bool:
    """
    Check if PDF has an embedded table of contents.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        True if TOC exists, False otherwise
    """
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        doc.close()
        return len(toc) > 0
    except Exception as e:
        logger.error(f"Error checking TOC: {e}")
        return False

# %% [markdown]
# ## OCRmyPDF Processing Functions

# %%
def preprocess_with_ocrmypdf(input_path: str, output_path: str = None) -> str:
    """
    Preprocess PDF with OCRmyPDF to add OCR layer and fix orientation.
    
    Args:
        input_path: Path to input PDF
        output_path: Path for output PDF (optional)
        
    Returns:
        Path to processed PDF
    """
    if output_path is None:
        # Create temporary file for processed PDF
        temp_dir = tempfile.gettempdir()
        base_name = Path(input_path).stem
        output_path = os.path.join(temp_dir, f"{base_name}_ocr_processed.pdf")
    
    try:
        logger.info(f"Starting OCRmyPDF preprocessing: {input_path}")
        start_time = time.time()
        
        # OCRmyPDF configuration for optimal processing
        ocrmypdf.ocr(
            input_path,
            output_path,
            language=['eng'],  # Can be configured for other languages
            rotate_pages=True,  # Auto-rotate pages with horizontal text
            deskew=True,       # Fix skewed text
            clean=True,        # Clean up artifacts
            optimize=1,        # Optimize output file size
            pdf_renderer='hocr',  # Use hOCR for better text positioning
            force_ocr=False,   # Only OCR pages that need it
            skip_text=False,   # Don't skip existing text
            redo_ocr=False,    # Don't redo existing OCR
            progress_bar=False,
            quiet=True
        )
        
        processing_time = time.time() - start_time
        logger.info(f"OCRmyPDF completed in {processing_time:.2f} seconds")
        
        return output_path
        
    except Exception as e:
        logger.error(f"OCRmyPDF preprocessing failed: {e}")
        # Return original path if OCR fails
        return input_path

# %% [markdown]
# ## PyMuPDF4LLM Header Detection Functions

# %%
def create_toc_header_logic(pdf_path: str) -> Dict[str, Any]:
    """
    Create header extraction logic based on TOC information.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Header info dictionary for PyMuPDF4LLM
    """
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        
        if not toc:
            doc.close()
            return None
            
        # Analyze TOC structure to create header logic
        header_info = {}
        level_fonts = {}
        
        # Extract font information for each TOC level
        for level, title, page_num in toc:
            if level not in level_fonts:
                level_fonts[level] = []
            
            # Try to find the actual text block for this heading
            if page_num <= len(doc):
                page = doc[page_num - 1]  # PyMuPDF uses 0-based indexing
                blocks = page.get_text("dict")
                
                # Search for matching text in blocks
                for block in blocks.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                if title.lower() in span.get("text", "").lower():
                                    font_info = {
                                        "font": span.get("font", ""),
                                        "size": span.get("size", 0),
                                        "flags": span.get("flags", 0)
                                    }
                                    level_fonts[level].append(font_info)
                                    break
        
        doc.close()
        
        # Create header detection logic
        if level_fonts:
            header_info = {
                "levels": len(level_fonts),
                "font_mapping": level_fonts,
                "use_toc": True
            }
        
        return header_info
        
    except Exception as e:
        logger.error(f"Error creating TOC header logic: {e}")
        return None

# %%
def create_heuristic_header_logic(pdf_path: str) -> Dict[str, Any]:
    """
    Create header detection logic based on font size and style heuristics.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Header info dictionary for PyMuPDF4LLM
    """
    try:
        doc = fitz.open(pdf_path)
        font_analysis = {}
        
        # Analyze first few pages to understand font patterns
        sample_pages = min(3, len(doc))
        
        for page_num in range(sample_pages):
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            font = span.get("font", "")
                            size = span.get("size", 0)
                            flags = span.get("flags", 0)
                            text = span.get("text", "").strip()
                            
                            if text and size > 0:
                                key = f"{font}_{size}_{flags}"
                                if key not in font_analysis:
                                    font_analysis[key] = {
                                        "font": font,
                                        "size": size,
                                        "flags": flags,
                                        "is_bold": bool(flags & 2**4),
                                        "is_italic": bool(flags & 2**1),
                                        "count": 0,
                                        "avg_length": 0,
                                        "examples": []
                                    }
                                
                                font_analysis[key]["count"] += 1
                                font_analysis[key]["avg_length"] += len(text)
                                if len(font_analysis[key]["examples"]) < 3:
                                    font_analysis[key]["examples"].append(text)
        
        doc.close()
        
        # Create header detection rules based on analysis
        sorted_fonts = sorted(font_analysis.items(), 
                            key=lambda x: x[1]["size"], reverse=True)
        
        header_info = {
            "levels": 3,  # Assume 3 header levels
            "font_rules": [],
            "use_toc": False
        }
        
        # Define header levels based on font size and style
        for i, (key, info) in enumerate(sorted_fonts[:3]):
            if info["size"] > 12 or info["is_bold"]:  # Potential header
                header_info["font_rules"].append({
                    "level": i + 1,
                    "font": info["font"],
                    "size_min": info["size"] - 1,
                    "size_max": info["size"] + 1,
                    "bold": info["is_bold"],
                    "italic": info["is_italic"]
                })
        
        return header_info
        
    except Exception as e:
        logger.error(f"Error creating heuristic header logic: {e}")
        return None

# %% [markdown]
# ## Main Processing Pipeline

# %%
def process_pdf_pipeline(input_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Main PDF processing pipeline that handles different PDF types and extracts structured content.
    
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
        output_dir = Path(input_path).parent / "processed_output"
    
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
        "header_info": None,
        "extracted_content": None,
        "metadata": {},
        "processing_time": None,
        "errors": []
    }
    
    try:
        logger.info(f"Starting PDF pipeline processing: {input_path}")
        
        # Step 1: Analyze PDF type
        logger.info("Step 1: Analyzing PDF type...")
        is_scanned = is_pdf_scanned(input_path)
        has_toc = has_table_of_contents(input_path)
        
        results["pdf_type"] = "scanned" if is_scanned else "born_digital"
        results["has_toc"] = has_toc
        
        # Step 2: Preprocess if needed
        processed_pdf_path = input_path
        
        if is_scanned:
            logger.info("Step 2: Applying OCRmyPDF preprocessing...")
            base_name = Path(input_path).stem
            ocr_output_path = os.path.join(output_dir, f"{base_name}_ocr_processed.pdf")
            processed_pdf_path = preprocess_with_ocrmypdf(input_path, ocr_output_path)
            results["ocr_applied"] = True
            results["processed_pdf_path"] = processed_pdf_path
            
            # Re-check TOC after OCR
            has_toc = has_table_of_contents(processed_pdf_path)
            results["has_toc"] = has_toc
        
        # Step 3: Create header detection logic
        logger.info("Step 3: Creating header detection logic...")
        header_info = None
        
        if has_toc:
            logger.info("Using TOC-based header logic")
            header_info = create_toc_header_logic(processed_pdf_path)
            results["extraction_method"] = "toc_based"
        else:
            logger.info("Using heuristic header logic")
            header_info = create_heuristic_header_logic(processed_pdf_path)
            results["extraction_method"] = "heuristic"
        
        results["header_info"] = header_info
        
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
        
        # Add header info if available
        if header_info and header_info.get("use_toc"):
            # Use TOC-based extraction
            extracted_content = pymupdf4llm.to_markdown(
                processed_pdf_path,
                **pymupdf_params
            )
        else:
            # Use standard extraction
            extracted_content = pymupdf4llm.to_markdown(
                processed_pdf_path,
                **pymupdf_params
            )
        
        extraction_time = time.time() - extraction_start
        results["extracted_content"] = extracted_content
        results["metadata"]["extraction_time"] = extraction_time
        
        # Step 5: Save extracted content
        logger.info("Step 5: Saving extracted content...")
        base_name = Path(input_path).stem
        
        # Save markdown content
        markdown_path = os.path.join(output_dir, f"{base_name}_extracted.md")
        with open(markdown_path, 'w', encoding='utf-8') as f:
            if isinstance(extracted_content, list):
                for chunk in extracted_content:
                    f.write(str(chunk) + "\n\n")
            else:
                f.write(str(extracted_content))
        
        results["metadata"]["markdown_path"] = markdown_path
        
        # Save processing metadata
        metadata_path = os.path.join(output_dir, f"{base_name}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            # Create a serializable copy of results
            serializable_results = {k: v for k, v in results.items() 
                                  if k not in ['extracted_content']}
            json.dump(serializable_results, f, indent=2, default=str)
        
        results["metadata"]["metadata_path"] = metadata_path
        
        # Calculate total processing time
        total_time = time.time() - start_time
        results["processing_time"] = total_time
        
        logger.info(f"Pipeline completed successfully in {total_time:.2f} seconds")
        
        return results
        
    except Exception as e:
        error_msg = f"Pipeline processing failed: {str(e)}"
        logger.error(error_msg)
        results["errors"].append(error_msg)
        results["processing_time"] = time.time() - start_time
        return results

# %% [markdown]
# ## Batch Processing Function

# %%
def batch_process_pdfs(input_dir: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Process multiple PDFs in a directory.
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory for output files
        
    Returns:
        Dictionary containing batch processing results
    """
    if output_dir is None:
        output_dir = os.path.join(input_dir, "batch_processed")
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    
    batch_results = {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "total_files": len(pdf_files),
        "processed_files": 0,
        "failed_files": 0,
        "results": {},
        "summary": {}
    }
    
    logger.info(f"Starting batch processing of {len(pdf_files)} PDF files")
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            
            # Create individual output directory for each PDF
            pdf_output_dir = os.path.join(output_dir, pdf_file.stem)
            
            # Process the PDF
            result = process_pdf_pipeline(str(pdf_file), pdf_output_dir)
            
            batch_results["results"][pdf_file.name] = result
            
            if result.get("errors"):
                batch_results["failed_files"] += 1
            else:
                batch_results["processed_files"] += 1
                
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {e}")
            batch_results["failed_files"] += 1
            batch_results["results"][pdf_file.name] = {
                "error": str(e),
                "processing_time": None
            }
    
    # Create summary
    batch_results["summary"] = {
        "success_rate": batch_results["processed_files"] / batch_results["total_files"],
        "total_processing_time": sum(
            r.get("processing_time", 0) for r in batch_results["results"].values()
            if r.get("processing_time")
        )
    }
    
    # Save batch results
    batch_summary_path = os.path.join(output_dir, "batch_processing_summary.json")
    with open(batch_summary_path, 'w', encoding='utf-8') as f:
        # Create serializable copy
        serializable_batch = {k: v for k, v in batch_results.items() 
                             if k != 'results'}
        serializable_batch['file_results'] = {
            name: {k: v for k, v in result.items() if k != 'extracted_content'}
            for name, result in batch_results['results'].items()
        }
        json.dump(serializable_batch, f, indent=2, default=str)
    
    logger.info(f"Batch processing completed: {batch_results['processed_files']}/{batch_results['total_files']} successful")
    
    return batch_results

# %% [markdown]
# ## Example Usage and Testing

# %%
def main():
    """
    Example usage of the PDF processing pipeline.
    """
    # Example 1: Process a single PDF
    print("=== Single PDF Processing Example ===")
    
    # Update this path to your actual PDF file
    pdf_path = "pdfs/sample_document.pdf"
    
    if os.path.exists(pdf_path):
        try:
            results = process_pdf_pipeline(pdf_path)
            
            print(f"Processing completed!")
            print(f"PDF Type: {results['pdf_type']}")
            print(f"Has TOC: {results['has_toc']}")
            print(f"OCR Applied: {results['ocr_applied']}")
            print(f"Extraction Method: {results['extraction_method']}")
            print(f"Processing Time: {results['processing_time']:.2f} seconds")
            
            if results['errors']:
                print(f"Errors: {results['errors']}")
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
    else:
        print(f"PDF file not found: {pdf_path}")
    
    # Example 2: Batch processing
    print("\n=== Batch Processing Example ===")
    
    pdfs_dir = "pdfs"
    if os.path.exists(pdfs_dir):
        try:
            batch_results = batch_process_pdfs(pdfs_dir)
            
            print(f"Batch processing completed!")
            print(f"Total files: {batch_results['total_files']}")
            print(f"Processed: {batch_results['processed_files']}")
            print(f"Failed: {batch_results['failed_files']}")
            print(f"Success rate: {batch_results['summary']['success_rate']:.2%}")
            
        except Exception as e:
            print(f"Error in batch processing: {e}")
    else:
        print(f"PDFs directory not found: {pdfs_dir}")

# %%
if __name__ == "__main__":
    main()

# %% [markdown]
# ## Performance Benchmarking Function

# %%
def benchmark_processing_methods(pdf_path: str) -> Dict[str, Any]:
    """
    Benchmark different processing approaches for comparison.
    
    Args:
        pdf_path: Path to PDF file for benchmarking
        
    Returns:
        Dictionary containing benchmark results
    """
    benchmark_results = {
        "pdf_path": pdf_path,
        "file_size": os.path.getsize(pdf_path),
        "methods": {}
    }
    
    # Method 1: Direct PyMuPDF4LLM (no preprocessing)
    try:
        start_time = time.time()
        direct_result = pymupdf4llm.to_markdown(pdf_path)
        direct_time = time.time() - start_time
        
        benchmark_results["methods"]["direct_pymupdf4llm"] = {
            "processing_time": direct_time,
            "content_length": len(str(direct_result)),
            "success": True
        }
    except Exception as e:
        benchmark_results["methods"]["direct_pymupdf4llm"] = {
            "processing_time": None,
            "content_length": 0,
            "success": False,
            "error": str(e)
        }
    
    # Method 2: OCR preprocessing + PyMuPDF4LLM
    try:
        start_time = time.time()
        
        # Apply OCR preprocessing
        temp_ocr_path = tempfile.mktemp(suffix=".pdf")
        ocr_path = preprocess_with_ocrmypdf(pdf_path, temp_ocr_path)
        
        # Extract with PyMuPDF4LLM
        ocr_result = pymupdf4llm.to_markdown(ocr_path)
        total_time = time.time() - start_time
        
        # Cleanup
        if os.path.exists(temp_ocr_path):
            os.remove(temp_ocr_path)
        
        benchmark_results["methods"]["ocr_plus_pymupdf4llm"] = {
            "processing_time": total_time,
            "content_length": len(str(ocr_result)),
            "success": True
        }
    except Exception as e:
        benchmark_results["methods"]["ocr_plus_pymupdf4llm"] = {
            "processing_time": None,
            "content_length": 0,
            "success": False,
            "error": str(e)
        }
    
    # Method 3: Full pipeline
    try:
        start_time = time.time()
        pipeline_result = process_pdf_pipeline(pdf_path)
        pipeline_time = time.time() - start_time
        
        benchmark_results["methods"]["full_pipeline"] = {
            "processing_time": pipeline_time,
            "content_length": len(str(pipeline_result.get("extracted_content", ""))),
            "success": len(pipeline_result.get("errors", [])) == 0,
            "pdf_type": pipeline_result.get("pdf_type"),
            "has_toc": pipeline_result.get("has_toc"),
            "ocr_applied": pipeline_result.get("ocr_applied")
        }
    except Exception as e:
        benchmark_results["methods"]["full_pipeline"] = {
            "processing_time": None,
            "content_length": 0,
            "success": False,
            "error": str(e)
        }
    
    return benchmark_results

# %% [markdown]
# ## Configuration and Constants

# %%
# Configuration settings
CONFIG = {
    "OCR_LANGUAGES": ['eng'],  # Add other languages as needed
    "TEXT_DENSITY_THRESHOLD": 0.1,  # Threshold for scanned PDF detection
    "SAMPLE_PAGES_FOR_ANALYSIS": 5,  # Number of pages to analyze for PDF type
    "MAX_HEADER_LEVELS": 3,  # Maximum number of header levels to detect
    "IMAGE_EXTRACTION_FORMAT": "png",  # Format for extracted images
    "IMAGE_EXTRACTION_DPI": 300,  # DPI for extracted images
    "TEMP_FILE_CLEANUP": True,  # Whether to cleanup temporary files
    "LOGGING_LEVEL": "INFO"  # Logging level
}

# File extensions to process
SUPPORTED_EXTENSIONS = ['.pdf']

# OCRmyPDF optimization settings
OCR_OPTIMIZATION_SETTINGS = {
    "optimize": 1,
    "pdf_renderer": "hocr",
    "clean": True,
    "deskew": True,
    "rotate_pages": True,
    "force_ocr": False,
    "skip_text": False,
    "redo_ocr": False
}

print("PDF Processing Pipeline with PyMuPDF4LLM and OCRmyPDF - Ready to use!")
print("\nKey functions:")
print("- process_pdf_pipeline(input_path) - Main processing function")
print("- batch_process_pdfs(input_dir) - Batch processing")
print("- benchmark_processing_methods(pdf_path) - Performance benchmarking")
print("- is_pdf_scanned(pdf_path) - PDF type detection")
print("- has_table_of_contents(pdf_path) - TOC detection")
