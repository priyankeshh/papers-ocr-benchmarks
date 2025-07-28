#!/usr/bin/env python3
"""
LitServe server for Enhanced AI OCR Extraction Pipeline
Serves the PDF processing pipeline as an API endpoint with file upload support.
"""

import os
import io
import base64
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

import litserve as ls
from fastapi import UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

# Import your pipeline functions
import fitz
import ocrmypdf
import pymupdf4llm
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedOCRAPI(ls.LitAPI):
    """
    LitServe API for Enhanced AI OCR Extraction Pipeline
    """
    
    def setup(self, device: str):
        """Initialize the pipeline components"""
        self.device = device
        logger.info(f"Setting up Enhanced OCR API on device: {device}")
        
        # Create necessary directories
        self.temp_dir = Path("temp_ocr")
        self.output_dir = Path("output_chunk")
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("Enhanced OCR API setup complete")

    def decode_request(self, request):
        """
        Decode incoming request containing PDF file and processing options
        Expected format: multipart/form-data with:
        - file: PDF file
        - chunk_mode: 'header' or 'llama_token' (optional, default: 'header')
        - chunk_size: int (optional, default: 1024)
        - chunk_overlap: int (optional, default: 128)
        - use_ocr: bool (optional, default: True for auto-detection)
        """
        try:
            # Extract file from request
            if hasattr(request, 'files') and 'file' in request.files:
                file = request.files['file']
            elif hasattr(request, 'file'):
                file = request.file
            else:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # Get processing options from form data or set defaults
            chunk_mode = getattr(request, 'chunk_mode', 'header')
            chunk_size = int(getattr(request, 'chunk_size', 1024))
            chunk_overlap = int(getattr(request, 'chunk_overlap', 128))
            use_ocr = getattr(request, 'use_ocr', 'auto')  # auto, true, false
            
            return {
                'file': file,
                'chunk_mode': chunk_mode,
                'chunk_size': chunk_size,
                'chunk_overlap': chunk_overlap,
                'use_ocr': use_ocr
            }
        except Exception as e:
            logger.error(f"Error decoding request: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")

    def predict(self, inputs):
        """Process the PDF through the enhanced OCR pipeline"""
        try:
            file = inputs['file']
            chunk_mode = inputs['chunk_mode']
            chunk_size = inputs['chunk_size']
            chunk_overlap = inputs['chunk_overlap']
            use_ocr = inputs['use_ocr']
            
            logger.info(f"Processing PDF with chunk_mode={chunk_mode}, chunk_size={chunk_size}")
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                if hasattr(file, 'read'):
                    content = file.read()
                elif hasattr(file, 'file'):
                    content = file.file.read()
                else:
                    content = file
                
                tmp_file.write(content)
                tmp_file.flush()
                temp_pdf_path = Path(tmp_file.name)
            
            try:
                # Process through pipeline
                chunks = self._process_pdf_pipeline(
                    temp_pdf_path,
                    chunk_mode=chunk_mode,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    use_ocr=use_ocr
                )
                
                # Clean up temporary file
                temp_pdf_path.unlink(missing_ok=True)
                
                return {
                    'status': 'success',
                    'chunks_count': len(chunks),
                    'chunks': chunks,
                    'processing_info': {
                        'chunk_mode': chunk_mode,
                        'chunk_size': chunk_size,
                        'chunk_overlap': chunk_overlap,
                        'use_ocr': use_ocr
                    }
                }
                
            except Exception as e:
                # Clean up temporary file on error
                temp_pdf_path.unlink(missing_ok=True)
                raise e
                
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'chunks_count': 0,
                'chunks': []
            }

    def encode_response(self, output):
        """Encode the response as JSON"""
        return JSONResponse(content=output)

    # Helper methods from your pipeline
    def _is_scanned_pdf(self, pdf_path):
        """Check if PDF is scanned (no selectable text)"""
        try:
            doc = fitz.open(str(pdf_path))
            is_scanned = all(not page.get_text().strip() for page in doc)
            doc.close()
            return is_scanned
        except Exception as e:
            logger.error(f"Error checking if PDF is scanned: {e}")
            return False

    def _preprocess_pdf(self, input_path, ocr_path, use_ocr='auto'):
        """Run OCRmyPDF only if needed"""
        try:
            if use_ocr == 'false':
                logger.info("OCR disabled by user, using original PDF")
                return input_path
            elif use_ocr == 'true':
                logger.info("OCR forced by user, running OCR")
                should_ocr = True
            else:  # auto
                should_ocr = self._is_scanned_pdf(input_path)
            
            if should_ocr:
                logger.info(f"Running OCR on PDF: {input_path}")
                ocrmypdf.ocr(
                    input_file=str(input_path),
                    output_file=str(ocr_path),
                    rotate_pages=True,
                    deskew=True,
                    force_ocr=True,
                    skip_text=True,
                    progress_bar=False
                )
                return ocr_path
            else:
                logger.info("Born-digital PDF detected, skipping OCR")
                return input_path
        except Exception as e:
            logger.error(f"Error during OCR preprocessing: {e}")
            raise

    def _remove_tables_from_markdown(self, md_text):
        """Remove markdown tables from text"""
        pattern = r'(?:^.*?\|.*?\n)(?:^[ \t]*\|?[-:]+[\| -:]+[\n\r])(?:^.*?\|.*?\n?)+'
        cleaned = re.sub(pattern, '', md_text, flags=re.MULTILINE)
        return cleaned

    def _chunk_by_section_headers(self, md_text, min_length=20):
        """Chunk markdown by section headers"""
        lines = md_text.splitlines()
        chunks = []
        current_chunk = []
        current_header = None
        start_line = 0
        
        for i, line in enumerate(lines):
            header_match = re.match(r"^(#+)\s+(.+)", line)
            if header_match:
                if current_chunk:
                    text = "\n".join(current_chunk).strip()
                    if len(text) >= min_length:
                        chunks.append({
                            "header": current_header,
                            "text": text,
                            "start_line": start_line,
                            "end_line": i-1,
                        })
                current_chunk = [line]
                current_header = header_match.group(2)
                start_line = i
            else:
                current_chunk.append(line)
                
        if current_chunk:
            text = "\n".join(current_chunk).strip()
            if len(text) >= min_length:
                chunks.append({
                    "header": current_header,
                    "text": text,
                    "start_line": start_line,
                    "end_line": len(lines)-1,
                })
        return chunks

    def _extract_and_chunk(self, pdf_path, chunk_mode='header', chunk_size=1024, chunk_overlap=128):
        """Extract markdown and chunk the content"""
        try:
            logger.info(f"Extracting markdown from {pdf_path}")
            
            # Extract markdown with TOC/hierarchy
            try:
                md_text = pymupdf4llm.to_markdown(
                    str(pdf_path),
                    include_toc=True,
                    write_images=False,
                )
            except TypeError:
                md_text = pymupdf4llm.to_markdown(
                    str(pdf_path),
                    include_toc=True,
                    write_images=False
                )
            
            # Remove tables
            md_text = self._remove_tables_from_markdown(md_text)
            
            # Choose chunking mode
            if chunk_mode == 'llama_token':
                # Use LlamaMarkdownReader's token-based chunking
                reader = pymupdf4llm.LlamaMarkdownReader(
                    margins=(0, 50, 0, 30),
                    max_levels=3,
                    body_limit=11,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                docs = reader.load_data(pdf_path)
                chunks = [
                    {
                        "text": self._remove_tables_from_markdown(doc.text),
                        "metadata": doc.extra_info
                    } for doc in docs
                ]
            else:
                # Manual header-based chunking
                section_chunks = self._chunk_by_section_headers(md_text, min_length=30)
                chunks = []
                for i, chunk in enumerate(section_chunks):
                    chunks.append({
                        "text": chunk["text"],
                        "metadata": {
                            "header": chunk["header"],
                            "source_pdf": str(pdf_path),
                            "chunk_index": i,
                            "start_line": chunk["start_line"],
                            "end_line": chunk["end_line"],
                        }
                    })
            
            logger.info(f"Produced {len(chunks)} chunks from {pdf_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Extraction/chunking error: {e}")
            raise

    def _process_pdf_pipeline(self, pdf_path, chunk_mode='header', chunk_size=1024, chunk_overlap=128, use_ocr='auto'):
        """Complete pipeline processing"""
        filename = Path(pdf_path).stem
        ocr_pdf = self.temp_dir / f"{filename}_ocr.pdf"
        
        try:
            # Step 1: Preprocess (OCR if necessary)
            used_pdf = self._preprocess_pdf(pdf_path, ocr_pdf, use_ocr=use_ocr)
            
            # Step 2: Extract and chunk
            chunks = self._extract_and_chunk(
                used_pdf, 
                chunk_mode=chunk_mode,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            logger.info(f"Pipeline completed: {len(chunks)} chunks extracted from {pdf_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Pipeline failed for {pdf_path}: {e}")
            raise


def create_server(
    port: int = 8001,
    host: str = "0.0.0.0",
    accelerator: str = "auto",
    workers_per_device: int = 1,
    timeout: int = 300
):
    """Create and configure the LitServe server"""
    
    # Create the API instance
    api = EnhancedOCRAPI()
    
    # Create the server
    server = ls.LitServer(
        api,
        accelerator=accelerator,
        workers_per_device=workers_per_device,
        timeout=timeout
    )
    
    return server


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced AI OCR Extraction Pipeline Server")
    parser.add_argument("--port", type=int, default=8001, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--accelerator", type=str, default="auto", help="Accelerator type (auto, cpu, gpu)")
    parser.add_argument("--workers", type=int, default=1, help="Workers per device")
    parser.add_argument("--timeout", type=int, default=300, help="Request timeout in seconds")
    
    args = parser.parse_args()
    
    print("🚀 Starting Enhanced AI OCR Extraction Pipeline Server...")
    print(f"📍 Server will be available at: http://{args.host}:{args.port}")
    print(f"⚡ Accelerator: {args.accelerator}")
    print(f"👥 Workers per device: {args.workers}")
    print(f"⏱️  Timeout: {args.timeout}s")
    
    # Create and run the server
    server = create_server(
        port=args.port,
        host=args.host,
        accelerator=args.accelerator,
        workers_per_device=args.workers,
        timeout=args.timeout
    )
    
    server.run(port=args.port, host=args.host)
