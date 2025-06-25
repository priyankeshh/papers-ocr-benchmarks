# OCR Benchmark for Scientific Literature - GPU Optimized Version
# GSoC Project: Enhanced AI OCR Extraction Pipeline
# Author: Priyankesh
# 
# This script compares 3 OCR systems with GPU acceleration when available
# Usage: python ocr_benchmark_gpu_optimized.py

#%% Cell 1: Setup and GPU Detection
import os
import time
import pandas as pd
import numpy as np
from pathlib import Path
import fitz  # PyMuPDF
import textdistance
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import torch

# GPU Detection and Setup
def setup_gpu_environment():
    """Setup GPU environment and return device configuration"""
    device_info = {
        'cuda_available': torch.cuda.is_available(),
        'device_count': 0,
        'device_name': 'CPU',
        'device': 'cpu'
    }
    
    if torch.cuda.is_available():
        device_info.update({
            'device_count': torch.cuda.device_count(),
            'device_name': torch.cuda.get_device_name(0),
            'device': 'cuda',
            'cuda_version': torch.version.cuda,
            'memory_total': torch.cuda.get_device_properties(0).total_memory / 1e9,
            'memory_reserved': torch.cuda.memory_reserved(0) / 1e9,
            'memory_allocated': torch.cuda.memory_allocated(0) / 1e9
        })
        
        print("🚀 GPU ACCELERATION ENABLED")
        print(f"   Device: {device_info['device_name']}")
        print(f"   CUDA Version: {device_info['cuda_version']}")
        print(f"   Total Memory: {device_info['memory_total']:.1f} GB")
        
        # Set optimal GPU settings
        torch.backends.cudnn.benchmark = True
        torch.cuda.empty_cache()
    else:
        print("⚠️  GPU not available - using CPU")
        print("   For GPU acceleration, ensure CUDA is properly installed")
    
    return device_info

# Initialize GPU environment
device_info = setup_gpu_environment()

print("🚀 OCR BENCHMARK FOR SCIENTIFIC LITERATURE - GPU OPTIMIZED")
print("=" * 70)
print("Comparing 3 OCR Systems: Docling, Marker, PyMuPDF")
print("Dataset: Scientific papers from ./pdfs directory")
print(f"Compute Device: {device_info['device_name']}")
print("=" * 70)

#%% Cell 2: GPU-Optimized OCR System Classes
class GPUOptimizedOCRSystem:
    """GPU-optimized OCR system with automatic device detection"""
    def __init__(self, name, device_info):
        self.name = name
        self.processing_time = 0
        self.device_info = device_info
        self.device = device_info['device']
        self.initialize()
    
    def initialize(self):
        """Initialize the OCR system with GPU optimization"""
        if self.name == "Docling":
            from docling.document_converter import DocumentConverter
            
            # GPU-optimized Docling configuration
            if self.device_info['cuda_available']:
                # Configure for GPU if available
                self.converter = DocumentConverter()
                print(f"✅ {self.name} initialized with GPU acceleration")
            else:
                self.converter = DocumentConverter()
                print(f"✅ {self.name} initialized (CPU mode)")
        
        elif self.name == "Marker":
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
            
            # GPU-optimized Marker configuration
            if self.device_info['cuda_available']:
                # Force GPU usage for Marker models
                os.environ['CUDA_VISIBLE_DEVICES'] = '0'
                model_dict = create_model_dict()
                self.converter = PdfConverter(
                    artifact_dict=model_dict,
                    processor_list=None,
                    renderer=None
                )
                print(f"✅ {self.name} initialized with GPU acceleration")
            else:
                model_dict = create_model_dict()
                self.converter = PdfConverter(
                    artifact_dict=model_dict,
                    processor_list=None,
                    renderer=None
                )
                print(f"✅ {self.name} initialized (CPU mode)")
        
        elif self.name == "PyMuPDF":
            print(f"✅ {self.name} initialized (CPU-based)")
    
    def extract_text(self, pdf_path):
        """Extract text from PDF with GPU optimization"""
        start_time = time.time()
        
        # Clear GPU cache before processing
        if self.device_info['cuda_available']:
            torch.cuda.empty_cache()
        
        try:
            if self.name == "Docling":
                result = self.converter.convert(str(pdf_path))
                text = result.document.export_to_markdown()
                
            elif self.name == "Marker":
                document = self.converter(str(pdf_path))
                # Handle different Marker API versions
                if hasattr(document, 'render'):
                    text = document.render()
                elif hasattr(document, 'markdown'):
                    text = document.markdown
                else:
                    text = str(document)
                    
            elif self.name == "PyMuPDF":
                doc = fitz.open(str(pdf_path))
                text = ""
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text += f"\n=== Page {page_num + 1} ===\n{page.get_text()}\n"
                doc.close()
            
            self.processing_time = time.time() - start_time
            
            # Log GPU memory usage if available
            if self.device_info['cuda_available']:
                memory_used = torch.cuda.memory_allocated(0) / 1e9
                print(f"    🔥 GPU Memory Used: {memory_used:.2f} GB")
            
            return text, {
                'status': 'success', 
                'processing_time': self.processing_time,
                'device': self.device,
                'gpu_memory_used': torch.cuda.memory_allocated(0) / 1e9 if self.device_info['cuda_available'] else 0
            }
            
        except Exception as e:
            self.processing_time = time.time() - start_time
            print(f"    ❌ {self.name} error: {str(e)}")
            return f"Error: {str(e)}", {
                'status': 'error', 
                'processing_time': self.processing_time,
                'device': self.device,
                'error': str(e)
            }
        finally:
            # Clean up GPU memory
            if self.device_info['cuda_available']:
                torch.cuda.empty_cache()

#%% Cell 3: Enhanced Evaluation Metrics
def calculate_text_metrics(reference_text, candidate_text):
    """Calculate comprehensive text comparison metrics"""
    if not reference_text or not candidate_text:
        return {
            'character_accuracy': 0.0,
            'word_accuracy': 0.0, 
            'length_ratio': 0.0,
            'word_count_ratio': 0.0,
            'line_count_ratio': 0.0
        }
    
    # Clean texts
    ref_clean = re.sub(r'\s+', ' ', reference_text.strip())
    cand_clean = re.sub(r'\s+', ' ', candidate_text.strip())
    
    # Character-level accuracy using Levenshtein distance
    char_distance = textdistance.levenshtein(ref_clean, cand_clean)
    max_len = max(len(ref_clean), len(cand_clean))
    char_accuracy = 1 - (char_distance / max_len) if max_len > 0 else 1.0
    
    # Word-level accuracy
    ref_words = reference_text.lower().split()
    cand_words = candidate_text.lower().split()
    
    if ref_words:
        word_distance = textdistance.levenshtein(ref_words, cand_words)
        word_accuracy = 1 - (word_distance / max(len(ref_words), len(cand_words)))
    else:
        word_accuracy = 1.0 if not cand_words else 0.0
    
    # Additional metrics
    length_ratio = len(candidate_text) / len(reference_text) if len(reference_text) > 0 else 0.0
    word_count_ratio = len(cand_words) / len(ref_words) if len(ref_words) > 0 else 0.0
    
    ref_lines = len(reference_text.split('\n'))
    cand_lines = len(candidate_text.split('\n'))
    line_count_ratio = cand_lines / ref_lines if ref_lines > 0 else 0.0
    
    return {
        'character_accuracy': max(0.0, char_accuracy),
        'word_accuracy': max(0.0, word_accuracy),
        'length_ratio': length_ratio,
        'word_count_ratio': word_count_ratio,
        'line_count_ratio': line_count_ratio
    }

def analyze_scientific_content(text):
    """Analyze scientific content preservation with enhanced patterns"""
    # Enhanced patterns for scientific content
    equations = len(re.findall(r'\$.*?\$|\\\(.*?\\\)|\\\[.*?\\\]|\\begin\{equation\}.*?\\end\{equation\}', text, re.DOTALL))
    citations = len(re.findall(r'\[[\d,\s-]+\]|\(\w+\s+et\s+al\.?,?\s+\d{4}\)|\(\w+,?\s+\d{4}\)', text))
    figures = len(re.findall(r'[Ff]igure\s+\d+|[Ff]ig\.?\s+\d+|Figure\s+[A-Z]', text))
    tables = len(re.findall(r'[Tt]able\s+\d+|Table\s+[A-Z]', text))
    formulas = len(re.findall(r'[A-Za-z]+\s*=\s*[A-Za-z0-9\+\-\*/\(\)]+', text))
    
    return {
        'equations_count': equations,
        'citations_count': citations,
        'figures_count': figures,
        'tables_count': tables,
        'formulas_count': formulas,
        'total_scientific_elements': equations + citations + figures + tables + formulas
    }

#%% Cell 4: GPU-Optimized Benchmark Runner
def run_gpu_optimized_benchmark():
    """Run the complete OCR benchmark with GPU optimization"""
    
    # Initialize GPU-optimized OCR systems
    systems = {
        'Docling': GPUOptimizedOCRSystem('Docling', device_info),
        'Marker': GPUOptimizedOCRSystem('Marker', device_info), 
        'PyMuPDF': GPUOptimizedOCRSystem('PyMuPDF', device_info)
    }
    
    # Find PDFs
    pdf_dir = Path('./pdfs')
    pdf_files = list(pdf_dir.glob('*.pdf'))
    
    if not pdf_files:
        print("❌ No PDFs found in ./pdfs directory!")
        return None, None
    
    print(f"\n📚 Found {len(pdf_files)} PDFs:")
    for pdf in pdf_files:
        print(f"  • {pdf.name}")
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"./output/gpu_benchmark_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Log system information
    system_info_file = output_dir / 'system_info.txt'
    with open(system_info_file, 'w') as f:
        f.write("GPU-Optimized OCR Benchmark System Information\n")
        f.write("=" * 50 + "\n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"CUDA Available: {device_info['cuda_available']}\n")
        f.write(f"Device: {device_info['device_name']}\n")
        if device_info['cuda_available']:
            f.write(f"CUDA Version: {device_info['cuda_version']}\n")
            f.write(f"GPU Memory: {device_info['memory_total']:.1f} GB\n")
        f.write(f"PyTorch Version: {torch.__version__}\n")
    
    # Run extractions with GPU monitoring
    all_extractions = {}
    
    for pdf_path in pdf_files:
        pdf_name = pdf_path.stem
        print(f"\n📖 Processing: {pdf_name}")
        print("-" * 60)
        
        extractions = {}
        
        for system_name, system in systems.items():
            print(f"🔄 {system_name}...")
            
            # Monitor GPU memory before processing
            if device_info['cuda_available']:
                memory_before = torch.cuda.memory_allocated(0) / 1e9
                print(f"    📊 GPU Memory Before: {memory_before:.2f} GB")
            
            text, metadata = system.extract_text(pdf_path)
            
            # Save extracted text with metadata
            output_file = output_dir / f"{pdf_name}_{system_name}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"OCR System: {system_name}\n")
                f.write(f"PDF: {pdf_name}\n")
                f.write(f"Processing Time: {metadata.get('processing_time', 0):.2f}s\n")
                f.write(f"Device: {metadata.get('device', 'unknown')}\n")
                f.write(f"GPU Memory Used: {metadata.get('gpu_memory_used', 0):.2f} GB\n")
                f.write(f"Status: {metadata.get('status', 'unknown')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(text)
            
            extractions[system_name] = {
                'text': text,
                'metadata': metadata
            }
            
            print(f"    ⏱️  Time: {metadata.get('processing_time', 0):.2f}s")
            print(f"    📝 Length: {len(text):,} chars")
            print(f"    💾 Saved: {output_file.name}")
        
        all_extractions[pdf_name] = extractions
    
    return all_extractions, output_dir

# Run the GPU-optimized benchmark
print("\n🚀 Starting GPU-Optimized OCR Benchmark...")
extractions, output_dir = run_gpu_optimized_benchmark()

if extractions:
    print(f"\n✅ Benchmark completed!")
    print(f"📁 Results saved to: {output_dir}")
else:
    print("❌ Benchmark failed!")

#%% Cell 5: Enhanced Metrics Calculation
def calculate_enhanced_metrics(extractions):
    """Calculate enhanced comparison metrics with GPU performance data"""
    
    results = []
    
    for pdf_name, pdf_extractions in extractions.items():
        if 'PyMuPDF' not in pdf_extractions:
            continue
            
        baseline_text = pdf_extractions['PyMuPDF']['text']
        baseline_scientific = analyze_scientific_content(baseline_text)
        
        for system_name, extraction in pdf_extractions.items():
            if system_name == 'PyMuPDF':
                continue  # Skip baseline comparison with itself
                
            if extraction['metadata']['status'] != 'success':
                continue
                
            # Text comparison metrics
            text_metrics = calculate_text_metrics(baseline_text, extraction['text'])
            
            # Scientific content analysis
            scientific_metrics = analyze_scientific_content(extraction['text'])
            
            result = {
                'PDF': pdf_name,
                'System': system_name,
                'Character_Accuracy': text_metrics['character_accuracy'],
                'Word_Accuracy': text_metrics['word_accuracy'],
                'Length_Ratio': text_metrics['length_ratio'],
                'Word_Count_Ratio': text_metrics['word_count_ratio'],
                'Processing_Time': extraction['metadata']['processing_time'],
                'Text_Length': len(extraction['text']),
                'Device': extraction['metadata'].get('device', 'unknown'),
                'GPU_Memory_Used': extraction['metadata'].get('gpu_memory_used', 0),
                'Equations_Found': scientific_metrics['equations_count'],
                'Citations_Found': scientific_metrics['citations_count'],
                'Figures_Found': scientific_metrics['figures_count'],
                'Tables_Found': scientific_metrics['tables_count'],
                'Formulas_Found': scientific_metrics['formulas_count'],
                'Scientific_Elements_Total': scientific_metrics['total_scientific_elements'],
                'Status': extraction['metadata']['status']
            }
            
            results.append(result)
    
    return pd.DataFrame(results)

# Calculate enhanced metrics
if extractions:
    results_df = calculate_enhanced_metrics(extractions)
    
    # Save results
    results_file = output_dir / 'gpu_benchmark_results.csv'
    results_df.to_csv(results_file, index=False)
    
    # Create enhanced summary with GPU metrics
    summary_df = results_df.groupby('System').agg({
        'Character_Accuracy': ['mean', 'std'],
        'Word_Accuracy': ['mean', 'std'], 
        'Processing_Time': ['mean', 'std'],
        'Text_Length': 'mean',
        'GPU_Memory_Used': 'mean',
        'Scientific_Elements_Total': 'mean'
    }).round(3)
    
    summary_file = output_dir / 'gpu_benchmark_summary.csv'
    summary_df.to_csv(summary_file)
    
    print("\n📊 GPU-OPTIMIZED BENCHMARK RESULTS")
    print("=" * 70)
    print(results_df.to_string(index=False))
    
    print(f"\n📈 SUMMARY STATISTICS")
    print("=" * 70)
    print(summary_df)
    
    print(f"\n💾 Files saved:")
    print(f"  📄 Detailed results: {results_file}")
    print(f"  📊 Summary: {summary_file}")
    print(f"  🖥️  System info: {output_dir / 'system_info.txt'}")

print("\n" + "="*70)
print("🎯 GPU-OPTIMIZED BENCHMARK READY!")
print("Copy each cell (marked with #%% Cell X) to Google Colab")
print("Or run this entire script with: python ocr_benchmark_gpu_optimized.py")
print("="*70)
