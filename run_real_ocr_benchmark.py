# Real OCR Benchmark - Using Actual Libraries
# This script uses real Docling, Marker, and Tesseract when available
# Author: Priyankesh
# 
# USAGE: python run_real_ocr_benchmark.py

import os
import time
import json
import pandas as pd
from pathlib import Path
import fitz  # PyMuPDF
import textdistance
import re
from datetime import datetime

# Check available OCR systems
def check_ocr_availability():
    """Check which OCR systems are actually available"""
    available_systems = {}
    
    # Check Docling
    try:
        from docling.document_converter import DocumentConverter
        available_systems['Docling'] = True
        print("✅ Docling available")
    except ImportError:
        available_systems['Docling'] = False
        print("⚠️  Docling not available")
    
    # Check Marker
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        available_systems['Marker'] = True
        print("✅ Marker available")
    except ImportError:
        available_systems['Marker'] = False
        print("⚠️  Marker not available")
    
    # Check Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        available_systems['Tesseract'] = True
        print("✅ Tesseract available")
    except:
        available_systems['Tesseract'] = False
        print("⚠️  Tesseract not available")
    
    # PyMuPDF is always available
    available_systems['PyMuPDF'] = True
    print("✅ PyMuPDF available")
    
    return available_systems

# Real OCR System Implementations
class RealOCRSystem:
    def __init__(self, name, available_systems):
        self.name = name
        self.processing_time = 0
        self.available_systems = available_systems
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the specific OCR system"""
        if self.name == "Docling" and self.available_systems['Docling']:
            from docling.document_converter import DocumentConverter
            self.converter = DocumentConverter()
            print(f"🔧 {self.name} initialized")
        
        elif self.name == "Marker" and self.available_systems['Marker']:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
            try:
                model_dict = create_model_dict()
                self.converter = PdfConverter(
                    artifact_dict=model_dict,
                    processor_list=None,
                    renderer=None
                )
                print(f"🔧 {self.name} initialized")
            except Exception as e:
                print(f"⚠️  {self.name} initialization failed: {e}")
                self.converter = None
        
        elif self.name == "Tesseract" and self.available_systems['Tesseract']:
            import pytesseract
            self.pytesseract = pytesseract
            print(f"🔧 {self.name} initialized")
        
        elif self.name == "PyMuPDF":
            # Always available
            print(f"🔧 {self.name} initialized")
        
        else:
            print(f"⚠️  {self.name} not available - will use fallback")
    
    def extract_text(self, pdf_path):
        """Extract text using the specific OCR system"""
        start_time = time.time()
        
        try:
            if self.name == "Docling" and self.available_systems['Docling']:
                return self._extract_with_docling(pdf_path, start_time)
            
            elif self.name == "Marker" and self.available_systems['Marker'] and hasattr(self, 'converter'):
                return self._extract_with_marker(pdf_path, start_time)
            
            elif self.name == "Tesseract" and self.available_systems['Tesseract']:
                return self._extract_with_tesseract(pdf_path, start_time)
            
            elif self.name == "PyMuPDF":
                return self._extract_with_pymupdf(pdf_path, start_time)
            
            else:
                # Fallback to PyMuPDF
                return self._extract_with_pymupdf(pdf_path, start_time)
        
        except Exception as e:
            self.processing_time = time.time() - start_time
            return f"Error: {str(e)}", {
                'status': 'error',
                'processing_time': self.processing_time,
                'method': self.name
            }
    
    def _extract_with_docling(self, pdf_path, start_time):
        """Extract using Docling"""
        print(f"  🔄 Processing with Docling...")

        # Convert Path to string for Docling
        pdf_path_str = str(pdf_path)
        result = self.converter.convert(pdf_path_str)
        markdown_text = result.document.export_to_markdown()

        self.processing_time = time.time() - start_time

        return markdown_text, {
            'processing_time': self.processing_time,
            'pages_processed': len(result.document.pages) if hasattr(result.document, 'pages') else 1,
            'status': 'success',
            'method': 'docling_actual',
            'format': 'markdown'
        }

    def _extract_with_marker(self, pdf_path, start_time):
        """Extract using Marker"""
        print(f"  🔄 Processing with Marker...")

        # Convert Path to string for Marker
        pdf_path_str = str(pdf_path)
        document = self.converter(pdf_path_str)
        full_text = document.render()

        self.processing_time = time.time() - start_time

        return full_text, {
            'processing_time': self.processing_time,
            'pages_processed': len(document.pages) if hasattr(document, 'pages') else 1,
            'status': 'success',
            'method': 'marker_actual',
            'format': 'markdown'
        }
    
    def _extract_with_tesseract(self, pdf_path, start_time):
        """Extract using Tesseract OCR"""
        print(f"  🔄 Processing with Tesseract...")

        # Convert Path to string for PyMuPDF
        pdf_path_str = str(pdf_path)
        doc = fitz.open(pdf_path_str)
        extracted_text = ""
        pages_count = len(doc)

        for page_num in range(pages_count):
            page = doc.load_page(page_num)

            # Convert to image
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
            img_data = pix.tobytes("png")

            # Convert to PIL Image
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(img_data))

            # OCR with Tesseract
            text = self.pytesseract.image_to_string(img, config='--psm 6')
            extracted_text += f"\n--- Page {page_num + 1} (Tesseract) ---\n{text}\n"

        doc.close()
        self.processing_time = time.time() - start_time

        return extracted_text, {
            'processing_time': self.processing_time,
            'pages_processed': pages_count,
            'status': 'success',
            'method': 'tesseract_actual'
        }
    
    def _extract_with_pymupdf(self, pdf_path, start_time):
        """Extract using PyMuPDF"""
        print(f"  🔄 Processing with PyMuPDF...")

        # Convert Path to string for PyMuPDF
        pdf_path_str = str(pdf_path)
        doc = fitz.open(pdf_path_str)
        extracted_text = ""
        pages_count = len(doc)

        for page_num in range(pages_count):
            page = doc.load_page(page_num)
            text = page.get_text()
            extracted_text += f"\n=== Page {page_num + 1} ===\n{text}\n"

        doc.close()
        self.processing_time = time.time() - start_time

        return extracted_text, {
            'processing_time': self.processing_time,
            'pages_processed': pages_count,
            'status': 'success',
            'method': 'pymupdf_direct'
        }

def setup_output_directories():
    """Create organized output directory structure"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output_dir = Path(f"./output/real_ocr_benchmark_{timestamp}")
    
    dirs = {
        'base': base_output_dir,
        'extracted_texts': base_output_dir / "extracted_texts",
        'comparisons': base_output_dir / "comparisons",
        'summaries': base_output_dir / "summaries"
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory created: {base_output_dir}")
    return dirs

def save_extracted_text(text, pdf_name, system_name, metadata, output_dirs):
    """Save extracted text with metadata"""
    filename = f"{pdf_name}_{system_name}.txt"
    filepath = output_dirs['extracted_texts'] / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"OCR System: {system_name}\n")
        f.write(f"PDF: {pdf_name}\n")
        f.write(f"Processing Time: {metadata.get('processing_time', 0):.2f} seconds\n")
        f.write(f"Method: {metadata.get('method', 'unknown')}\n")
        f.write(f"Status: {metadata.get('status', 'unknown')}\n")
        f.write(f"Extraction Time: {datetime.now()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(text)
    
    print(f"    💾 Saved: {filename} ({len(text)} chars)")
    return filepath

def calculate_basic_metrics(ground_truth, predicted):
    """Calculate basic comparison metrics"""
    if not ground_truth or not predicted:
        return {'char_accuracy': 0.0, 'word_accuracy': 0.0, 'length_ratio': 0.0}
    
    # Character accuracy
    gt_clean = re.sub(r'\s+', ' ', ground_truth.strip())
    pred_clean = re.sub(r'\s+', ' ', predicted.strip())
    
    char_distance = textdistance.levenshtein(gt_clean, pred_clean)
    max_len = max(len(gt_clean), len(pred_clean))
    char_accuracy = 1 - (char_distance / max_len) if max_len > 0 else 1.0
    
    # Word accuracy
    gt_words = ground_truth.lower().split()
    pred_words = predicted.lower().split()
    
    if gt_words:
        word_distance = textdistance.levenshtein(gt_words, pred_words)
        word_accuracy = 1 - (word_distance / max(len(gt_words), len(pred_words)))
    else:
        word_accuracy = 1.0 if not pred_words else 0.0
    
    # Length ratio
    length_ratio = len(predicted) / len(ground_truth) if len(ground_truth) > 0 else 0.0
    
    return {
        'char_accuracy': max(0.0, char_accuracy),
        'word_accuracy': max(0.0, word_accuracy),
        'length_ratio': length_ratio
    }

def run_real_ocr_benchmark():
    """Run benchmark using real OCR systems"""
    
    print("🚀 REAL OCR BENCHMARK")
    print("=" * 60)
    
    # Check available systems
    available_systems = check_ocr_availability()
    
    # Setup output directories
    output_dirs = setup_output_directories()
    
    # Initialize available OCR systems
    systems = {}
    for system_name in ['Docling', 'Marker', 'Tesseract', 'PyMuPDF']:
        if available_systems.get(system_name, False):
            systems[system_name] = RealOCRSystem(system_name, available_systems)
    
    print(f"\n🔧 Initialized {len(systems)} OCR systems:")
    for system_name in systems.keys():
        print(f"  • {system_name}")
    
    # Find PDFs
    pdf_dir = Path('./pdfs')
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    if not pdf_files:
        print("❌ No PDFs found in ./pdfs directory!")
        return
    
    print(f"\n📚 Found {len(pdf_files)} PDFs:")
    for pdf in pdf_files:
        print(f"  • {pdf.name}")
    
    # Run benchmark
    all_results = []
    
    for pdf_path in pdf_files:
        pdf_name = pdf_path.stem
        print(f"\n📖 Processing: {pdf_name}")
        print("-" * 50)
        
        # Extract with each system
        extractions = {}
        
        for system_name, system in systems.items():
            print(f"🔄 {system_name}...")
            
            extracted_text, metadata = system.extract_text(pdf_path)
            
            # Save extracted text
            save_extracted_text(extracted_text, pdf_name, system_name, metadata, output_dirs)
            
            extractions[system_name] = {
                'text': extracted_text,
                'metadata': metadata
            }
            
            print(f"    ⏱️  Time: {metadata.get('processing_time', 0):.2f}s")
        
        # Calculate comparisons (using PyMuPDF as baseline)
        if 'PyMuPDF' in extractions:
            baseline_text = extractions['PyMuPDF']['text']
            
            for system_name, extraction in extractions.items():
                if system_name != 'PyMuPDF':
                    metrics = calculate_basic_metrics(baseline_text, extraction['text'])
                    
                    result = {
                        'PDF': pdf_name,
                        'System': system_name,
                        'Character_Accuracy': metrics['char_accuracy'],
                        'Word_Accuracy': metrics['word_accuracy'],
                        'Length_Ratio': metrics['length_ratio'],
                        'Processing_Time': extraction['metadata'].get('processing_time', 0),
                        'Text_Length': len(extraction['text']),
                        'Status': extraction['metadata'].get('status', 'unknown')
                    }
                    
                    all_results.append(result)
    
    # Save results
    if all_results:
        results_df = pd.DataFrame(all_results)
        results_file = output_dirs['summaries'] / 'real_benchmark_results.csv'
        results_df.to_csv(results_file, index=False)
        
        # Create summary
        summary_df = results_df.groupby('System').agg({
            'Character_Accuracy': 'mean',
            'Word_Accuracy': 'mean',
            'Length_Ratio': 'mean',
            'Processing_Time': 'mean',
            'Text_Length': 'mean'
        }).round(3)
        
        summary_file = output_dirs['summaries'] / 'real_benchmark_summary.csv'
        summary_df.to_csv(summary_file)
        
        print(f"\n📊 BENCHMARK SUMMARY")
        print("=" * 60)
        print(summary_df)
        
        print(f"\n✅ BENCHMARK COMPLETE!")
        print(f"📁 All outputs saved to: {output_dirs['base']}")
        print(f"📄 Extracted texts: {output_dirs['extracted_texts']}")
        print(f"📊 Results: {results_file}")
        print(f"📈 Summary: {summary_file}")
        
        return output_dirs, results_df, summary_df
    else:
        print("\n⚠️  No results to save - check OCR system availability")
        return output_dirs, None, None

if __name__ == "__main__":
    output_dirs, results_df, summary_df = run_real_ocr_benchmark()
