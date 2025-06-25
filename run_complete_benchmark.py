# Complete OCR Benchmark - EXECUTABLE VERSION
# This script actually runs the benchmark and saves all outputs
# Author: Priyankesh
# 
# USAGE: python run_complete_benchmark.py

import os
import time
import json
import pandas as pd
import numpy as np
from pathlib import Path
import fitz  # PyMuPDF
import textdistance
import re
from datetime import datetime

# Create output directory structure
def setup_output_directories():
    """Create organized output directory structure"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output_dir = Path(f"./output/benchmark_run_{timestamp}")
    
    # Create subdirectories
    dirs = {
        'base': base_output_dir,
        'extracted_texts': base_output_dir / "extracted_texts",
        'metrics': base_output_dir / "metrics", 
        'comparisons': base_output_dir / "comparisons",
        'summaries': base_output_dir / "summaries"
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory created: {base_output_dir}")
    return dirs

# Simple OCR Systems (working implementations)
class SimpleOCRSystem:
    def __init__(self, name):
        self.name = name
        self.processing_time = 0
    
    def extract_text(self, pdf_path):
        start_time = time.time()
        
        try:
            doc = fitz.open(pdf_path)
            extracted_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Apply different processing based on system
                if self.name == "PyMuPDF_Direct":
                    # Direct text extraction
                    extracted_text += f"\n=== PAGE {page_num + 1} ===\n{text}\n"
                
                elif self.name == "PyMuPDF_Enhanced":
                    # Enhanced with structure preservation
                    text_dict = page.get_text("dict")
                    structured_text = self._extract_structured(text_dict)
                    extracted_text += f"\n=== PAGE {page_num + 1} (Enhanced) ===\n{structured_text}\n"
                
                elif self.name == "Marker_Simulation":
                    # Simulate Marker's high-quality extraction
                    enhanced_text = self._simulate_marker_quality(text)
                    extracted_text += f"\n=== PAGE {page_num + 1} (Marker Style) ===\n{enhanced_text}\n"
                
                elif self.name == "Docling_Simulation":
                    # Simulate Docling's layout analysis
                    layout_text = self._simulate_docling_layout(text)
                    extracted_text += f"\n## Page {page_num + 1}\n\n{layout_text}\n"
            
            doc.close()
            self.processing_time = time.time() - start_time
            
            return extracted_text, {
                'processing_time': self.processing_time,
                'pages_processed': len(doc),
                'status': 'success',
                'method': self.name
            }
            
        except Exception as e:
            self.processing_time = time.time() - start_time
            return f"Error: {str(e)}", {
                'status': 'error', 
                'processing_time': self.processing_time,
                'method': self.name
            }
    
    def _extract_structured(self, text_dict):
        """Extract text with basic structure preservation"""
        blocks = []
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                block_text = ""
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                    block_text += line_text + "\n"
                blocks.append(block_text.strip())
        return "\n\n".join(blocks)
    
    def _simulate_marker_quality(self, text):
        """Simulate Marker's high-quality text extraction"""
        # Add some structure and clean up
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Simulate better formatting
                if len(line.split()) <= 8 and line.isupper():
                    processed_lines.append(f"# {line}")  # Header
                elif line.endswith(':'):
                    processed_lines.append(f"## {line}")  # Subheader
                else:
                    processed_lines.append(line)
        
        return "\n\n".join(processed_lines)
    
    def _simulate_docling_layout(self, text):
        """Simulate Docling's advanced layout analysis"""
        lines = text.split('\n')
        markdown_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Simulate markdown conversion
                if len(line.split()) <= 6 and (line.isupper() or line.istitle()):
                    markdown_lines.append(f"### {line}")
                elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    markdown_lines.append(f"1. {line[2:].strip()}")
                elif line.startswith(('-', '•', '*')):
                    markdown_lines.append(f"- {line[1:].strip()}")
                else:
                    markdown_lines.append(line)
        
        return "\n\n".join(markdown_lines)

# Metrics calculation
def calculate_character_accuracy(ground_truth, predicted):
    """Calculate character-level accuracy"""
    if not ground_truth or not predicted:
        return 0.0
    
    gt_clean = re.sub(r'\s+', ' ', ground_truth.strip())
    pred_clean = re.sub(r'\s+', ' ', predicted.strip())
    
    distance = textdistance.levenshtein(gt_clean, pred_clean)
    max_len = max(len(gt_clean), len(pred_clean))
    
    if max_len == 0:
        return 1.0
    
    accuracy = 1 - (distance / max_len)
    return max(0.0, accuracy)

def calculate_word_accuracy(ground_truth, predicted):
    """Calculate word-level accuracy"""
    if not ground_truth or not predicted:
        return 0.0
        
    gt_words = ground_truth.lower().split()
    pred_words = predicted.lower().split()
    
    if not gt_words:
        return 1.0 if not pred_words else 0.0
    
    distance = textdistance.levenshtein(gt_words, pred_words)
    accuracy = 1 - (distance / max(len(gt_words), len(pred_words)))
    return max(0.0, accuracy)

def calculate_scientific_accuracy(ground_truth, predicted):
    """Calculate scientific notation accuracy"""
    patterns = [
        r'\d+\.\d+%',              # Percentages
        r'p\s*[<>=]\s*0\.\d+',    # P-values
        r'[α-ωΑ-Ω]',              # Greek letters
        r'[±×÷≤≥≠≈]',             # Math symbols
        r'\d+\.\d+[eE][+-]?\d+',  # Scientific notation
    ]
    
    gt_matches = set()
    pred_matches = set()
    
    for pattern in patterns:
        gt_matches.update(re.findall(pattern, ground_truth, re.IGNORECASE))
        pred_matches.update(re.findall(pattern, predicted, re.IGNORECASE))
    
    if not gt_matches:
        return 1.0 if not pred_matches else 0.0
    
    intersection = len(gt_matches & pred_matches)
    union = len(gt_matches | pred_matches)
    
    return intersection / union if union > 0 else 1.0

def save_extracted_text(text, pdf_name, system_name, output_dirs):
    """Save extracted text to file"""
    filename = f"{pdf_name}_{system_name}.txt"
    filepath = output_dirs['extracted_texts'] / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"OCR System: {system_name}\n")
        f.write(f"PDF: {pdf_name}\n")
        f.write(f"Extraction Time: {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        f.write(text)
    
    print(f"  💾 Saved: {filename}")
    return filepath

def run_complete_benchmark():
    """Run the complete OCR benchmark with outputs"""
    
    print("🚀 COMPLETE OCR BENCHMARK")
    print("=" * 60)
    
    # Setup output directories
    output_dirs = setup_output_directories()
    
    # Initialize OCR systems
    systems = {
        'PyMuPDF_Direct': SimpleOCRSystem("PyMuPDF_Direct"),
        'PyMuPDF_Enhanced': SimpleOCRSystem("PyMuPDF_Enhanced"), 
        'Marker_Simulation': SimpleOCRSystem("Marker_Simulation"),
        'Docling_Simulation': SimpleOCRSystem("Docling_Simulation")
    }
    
    print(f"🔧 Initialized {len(systems)} OCR systems:")
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
        print("-" * 40)
        
        # Create ground truth (using first system)
        ground_truth_system = systems['PyMuPDF_Direct']
        gt_text, gt_meta = ground_truth_system.extract_text(pdf_path)
        
        # Save ground truth
        save_extracted_text(gt_text, pdf_name, "GroundTruth", output_dirs)
        
        for system_name, system in systems.items():
            print(f"  🔄 {system_name}...")
            
            # Extract text
            extracted_text, metadata = system.extract_text(pdf_path)
            
            # Save extracted text
            save_extracted_text(extracted_text, pdf_name, system_name, output_dirs)
            
            if metadata['status'] == 'success':
                # Calculate metrics
                char_acc = calculate_character_accuracy(gt_text, extracted_text)
                word_acc = calculate_word_accuracy(gt_text, extracted_text)
                sci_acc = calculate_scientific_accuracy(gt_text, extracted_text)
                
                result = {
                    'PDF': pdf_name,
                    'System': system_name,
                    'Character_Accuracy': char_acc,
                    'Word_Accuracy': word_acc,
                    'Scientific_Accuracy': sci_acc,
                    'Processing_Time': metadata['processing_time'],
                    'Pages_Processed': metadata['pages_processed'],
                    'Text_Length': len(extracted_text),
                    'Status': 'Success'
                }
                
                print(f"    ✅ Char: {char_acc:.3f}, Word: {word_acc:.3f}, Sci: {sci_acc:.3f}, Time: {metadata['processing_time']:.2f}s")
            else:
                result = {
                    'PDF': pdf_name,
                    'System': system_name,
                    'Character_Accuracy': 0.0,
                    'Word_Accuracy': 0.0,
                    'Scientific_Accuracy': 0.0,
                    'Processing_Time': metadata['processing_time'],
                    'Pages_Processed': 0,
                    'Text_Length': 0,
                    'Status': 'Error'
                }
                print(f"    ❌ Error in processing")
            
            all_results.append(result)
    
    # Save results
    results_df = pd.DataFrame(all_results)
    results_file = output_dirs['summaries'] / 'benchmark_results.csv'
    results_df.to_csv(results_file, index=False)
    
    # Create summary
    summary_df = results_df.groupby('System').agg({
        'Character_Accuracy': 'mean',
        'Word_Accuracy': 'mean', 
        'Scientific_Accuracy': 'mean',
        'Processing_Time': 'mean',
        'Pages_Processed': 'sum',
        'Text_Length': 'mean'
    }).round(3)
    
    summary_file = output_dirs['summaries'] / 'benchmark_summary.csv'
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

if __name__ == "__main__":
    output_dirs, results_df, summary_df = run_complete_benchmark()
