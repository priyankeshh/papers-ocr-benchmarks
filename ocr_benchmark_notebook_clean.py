# OCR Benchmark for Scientific Literature - Clean Version
# GSoC Project: Enhanced AI OCR Extraction Pipeline
# Author: Priyankesh
# 
# This script compares 3 OCR systems: Docling, Marker, and PyMuPDF
# Usage: Copy each cell to Google Colab or run as Python script

#%% Cell 1: Setup and Imports
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

print("🚀 OCR BENCHMARK FOR SCIENTIFIC LITERATURE")
print("=" * 60)
print("Comparing 3 OCR Systems: Docling, Marker, PyMuPDF")
print("Dataset: Scientific papers from ./pdfs directory")
print("=" * 60)

#%% Cell 2: OCR System Classes
class OCRSystem:
    """Base class for OCR systems"""
    def __init__(self, name):
        self.name = name
        self.processing_time = 0
        self.initialize()
    
    def initialize(self):
        """Initialize the OCR system"""
        if self.name == "Docling":
            from docling.document_converter import DocumentConverter
            self.converter = DocumentConverter()
            print(f"✅ {self.name} initialized")
        
        elif self.name == "Marker":
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
            model_dict = create_model_dict()
            self.converter = PdfConverter(
                artifact_dict=model_dict,
                processor_list=None,
                renderer=None
            )
            print(f"✅ {self.name} initialized")
        
        elif self.name == "PyMuPDF":
            print(f"✅ {self.name} initialized")
    
    def extract_text(self, pdf_path):
        """Extract text from PDF"""
        start_time = time.time()
        
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
            return text, {'status': 'success', 'processing_time': self.processing_time}
            
        except Exception as e:
            self.processing_time = time.time() - start_time
            return f"Error: {str(e)}", {'status': 'error', 'processing_time': self.processing_time}

#%% Cell 3: Evaluation Metrics
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
    
    # Character-level accuracy
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
    """Analyze scientific content preservation"""
    # Count scientific elements
    equations = len(re.findall(r'\$.*?\$|\\\(.*?\\\)|\\\[.*?\\\]', text))
    citations = len(re.findall(r'\[[\d,\s-]+\]|\(\w+\s+et\s+al\.?,?\s+\d{4}\)', text))
    figures = len(re.findall(r'[Ff]igure\s+\d+|[Ff]ig\.?\s+\d+', text))
    tables = len(re.findall(r'[Tt]able\s+\d+', text))
    
    return {
        'equations_count': equations,
        'citations_count': citations,
        'figures_count': figures,
        'tables_count': tables,
        'total_scientific_elements': equations + citations + figures + tables
    }

#%% Cell 4: Run Benchmark
def run_ocr_benchmark():
    """Run the complete OCR benchmark"""
    
    # Initialize OCR systems
    systems = {
        'Docling': OCRSystem('Docling'),
        'Marker': OCRSystem('Marker'), 
        'PyMuPDF': OCRSystem('PyMuPDF')
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
    output_dir = Path(f"./output/clean_benchmark_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run extractions
    all_results = []
    all_extractions = {}
    
    for pdf_path in pdf_files:
        pdf_name = pdf_path.stem
        print(f"\n📖 Processing: {pdf_name}")
        print("-" * 50)
        
        extractions = {}
        
        for system_name, system in systems.items():
            print(f"🔄 {system_name}...")
            
            text, metadata = system.extract_text(pdf_path)
            extractions[system_name] = {
                'text': text,
                'metadata': metadata
            }
            
            # Save extracted text
            output_file = output_dir / f"{pdf_name}_{system_name}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"OCR System: {system_name}\n")
                f.write(f"PDF: {pdf_name}\n")
                f.write(f"Processing Time: {metadata.get('processing_time', 0):.2f}s\n")
                f.write(f"Status: {metadata.get('status', 'unknown')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(text)
            
            print(f"    ⏱️  Time: {metadata.get('processing_time', 0):.2f}s")
            print(f"    📝 Length: {len(text):,} chars")
        
        all_extractions[pdf_name] = extractions
    
    return all_extractions, output_dir

# Run the benchmark
print("\n🚀 Starting OCR Benchmark...")
extractions, output_dir = run_ocr_benchmark()

if extractions:
    print(f"\n✅ Benchmark completed!")
    print(f"📁 Results saved to: {output_dir}")
else:
    print("❌ Benchmark failed!")

#%% Cell 5: Calculate Comparison Metrics
def calculate_comparison_metrics(extractions):
    """Calculate comparison metrics using PyMuPDF as baseline"""
    
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
                'Equations_Found': scientific_metrics['equations_count'],
                'Citations_Found': scientific_metrics['citations_count'],
                'Figures_Found': scientific_metrics['figures_count'],
                'Tables_Found': scientific_metrics['tables_count'],
                'Scientific_Elements_Total': scientific_metrics['total_scientific_elements'],
                'Status': extraction['metadata']['status']
            }
            
            results.append(result)
    
    return pd.DataFrame(results)

# Calculate metrics
if extractions:
    results_df = calculate_comparison_metrics(extractions)
    
    # Save results
    results_file = output_dir / 'benchmark_results.csv'
    results_df.to_csv(results_file, index=False)
    
    # Create summary
    summary_df = results_df.groupby('System').agg({
        'Character_Accuracy': ['mean', 'std'],
        'Word_Accuracy': ['mean', 'std'], 
        'Processing_Time': ['mean', 'std'],
        'Text_Length': 'mean',
        'Scientific_Elements_Total': 'mean'
    }).round(3)
    
    summary_file = output_dir / 'benchmark_summary.csv'
    summary_df.to_csv(summary_file)
    
    print("\n📊 BENCHMARK RESULTS")
    print("=" * 60)
    print(results_df.to_string(index=False))
    
    print(f"\n📈 SUMMARY STATISTICS")
    print("=" * 60)
    print(summary_df)
    
    print(f"\n💾 Files saved:")
    print(f"  📄 Detailed results: {results_file}")
    print(f"  📊 Summary: {summary_file}")

#%% Cell 6: Visualization and Analysis
def create_benchmark_visualizations(results_df, output_dir):
    """Create comprehensive visualizations of benchmark results"""

    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('OCR Systems Benchmark Results', fontsize=16, fontweight='bold')

    # 1. Accuracy Comparison
    ax1 = axes[0, 0]
    accuracy_data = results_df.groupby('System')[['Character_Accuracy', 'Word_Accuracy']].mean()
    accuracy_data.plot(kind='bar', ax=ax1, color=['skyblue', 'lightcoral'])
    ax1.set_title('Text Accuracy Comparison')
    ax1.set_ylabel('Accuracy Score')
    ax1.set_xlabel('OCR System')
    ax1.legend(['Character Accuracy', 'Word Accuracy'])
    ax1.tick_params(axis='x', rotation=45)

    # 2. Processing Time Comparison
    ax2 = axes[0, 1]
    time_data = results_df.groupby('System')['Processing_Time'].mean()
    time_data.plot(kind='bar', ax=ax2, color='lightgreen')
    ax2.set_title('Average Processing Time')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_xlabel('OCR System')
    ax2.tick_params(axis='x', rotation=45)

    # 3. Scientific Content Detection
    ax3 = axes[1, 0]
    scientific_data = results_df.groupby('System')['Scientific_Elements_Total'].mean()
    scientific_data.plot(kind='bar', ax=ax3, color='gold')
    ax3.set_title('Scientific Elements Detection')
    ax3.set_ylabel('Average Elements Found')
    ax3.set_xlabel('OCR System')
    ax3.tick_params(axis='x', rotation=45)

    # 4. Text Length Comparison
    ax4 = axes[1, 1]
    length_data = results_df.groupby('System')['Text_Length'].mean()
    length_data.plot(kind='bar', ax=ax4, color='plum')
    ax4.set_title('Average Text Length')
    ax4.set_ylabel('Characters')
    ax4.set_xlabel('OCR System')
    ax4.tick_params(axis='x', rotation=45)

    plt.tight_layout()

    # Save plot
    plot_file = output_dir / 'benchmark_visualization.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"📊 Visualization saved: {plot_file}")

    return plot_file

def generate_benchmark_report(results_df, output_dir):
    """Generate a comprehensive benchmark report"""

    report = []
    report.append("# OCR BENCHMARK REPORT FOR SCIENTIFIC LITERATURE")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Dataset: {len(results_df['PDF'].unique())} scientific papers")
    report.append(f"Systems tested: {', '.join(results_df['System'].unique())}")
    report.append("")

    # Executive Summary
    report.append("## EXECUTIVE SUMMARY")
    report.append("-" * 30)

    # Best performing system
    avg_scores = results_df.groupby('System').agg({
        'Character_Accuracy': 'mean',
        'Word_Accuracy': 'mean',
        'Processing_Time': 'mean'
    })

    best_accuracy = avg_scores['Character_Accuracy'].idxmax()
    fastest_system = avg_scores['Processing_Time'].idxmin()

    report.append(f"🏆 Best Accuracy: {best_accuracy} ({avg_scores.loc[best_accuracy, 'Character_Accuracy']:.1%} character accuracy)")
    report.append(f"⚡ Fastest System: {fastest_system} ({avg_scores.loc[fastest_system, 'Processing_Time']:.1f}s average)")
    report.append("")

    # Detailed Results
    report.append("## DETAILED RESULTS")
    report.append("-" * 30)

    for system in results_df['System'].unique():
        system_data = results_df[results_df['System'] == system]

        report.append(f"### {system}")
        report.append(f"- Character Accuracy: {system_data['Character_Accuracy'].mean():.1%} ± {system_data['Character_Accuracy'].std():.1%}")
        report.append(f"- Word Accuracy: {system_data['Word_Accuracy'].mean():.1%} ± {system_data['Word_Accuracy'].std():.1%}")
        report.append(f"- Processing Time: {system_data['Processing_Time'].mean():.1f}s ± {system_data['Processing_Time'].std():.1f}s")
        report.append(f"- Scientific Elements: {system_data['Scientific_Elements_Total'].mean():.1f} avg per document")
        report.append("")

    # Recommendations
    report.append("## RECOMMENDATIONS")
    report.append("-" * 30)
    report.append("Based on the benchmark results:")
    report.append("")

    if best_accuracy == fastest_system:
        report.append(f"✅ {best_accuracy} is recommended as it provides the best balance of accuracy and speed.")
    else:
        report.append(f"⚖️  Choose {best_accuracy} for highest accuracy or {fastest_system} for fastest processing.")

    report.append("")
    report.append("For scientific literature processing:")
    report.append("- All systems preserve basic text structure")
    report.append("- Consider post-processing for scientific notation and formulas")
    report.append("- Validate results on domain-specific content")

    # Save report
    report_file = output_dir / 'benchmark_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"📋 Report saved: {report_file}")
    return report_file

# Generate visualizations and report
if extractions and not results_df.empty:
    print("\n🎨 Creating visualizations...")
    plot_file = create_benchmark_visualizations(results_df, output_dir)

    print("\n📋 Generating report...")
    report_file = generate_benchmark_report(results_df, output_dir)

    print(f"\n🎉 BENCHMARK COMPLETE!")
    print(f"📁 All files saved to: {output_dir}")
    print(f"📊 View results: {plot_file}")
    print(f"📋 Read report: {report_file}")

#%% Cell 7: Quick Analysis Functions
def quick_comparison():
    """Quick comparison of the 3 OCR systems"""
    if 'results_df' in globals() and not results_df.empty:
        print("🔍 QUICK COMPARISON")
        print("=" * 40)

        comparison = results_df.groupby('System').agg({
            'Character_Accuracy': 'mean',
            'Processing_Time': 'mean',
            'Text_Length': 'mean'
        }).round(3)

        comparison['Accuracy_Rank'] = comparison['Character_Accuracy'].rank(ascending=False)
        comparison['Speed_Rank'] = comparison['Processing_Time'].rank(ascending=True)

        print(comparison)

        return comparison
    else:
        print("❌ No results available. Run the benchmark first.")
        return None

def system_details(system_name):
    """Get detailed results for a specific system"""
    if 'results_df' in globals() and not results_df.empty:
        system_data = results_df[results_df['System'] == system_name]
        if not system_data.empty:
            print(f"📊 DETAILED RESULTS FOR {system_name}")
            print("=" * 50)
            print(system_data.to_string(index=False))
        else:
            print(f"❌ No data found for system: {system_name}")
    else:
        print("❌ No results available. Run the benchmark first.")

# Run quick comparison
quick_comparison()

print("\n" + "="*60)
print("🎯 NOTEBOOK READY FOR COLAB!")
print("Copy each cell (marked with #%% Cell X) to Google Colab")
print("Or run this entire script with: python ocr_benchmark_notebook_clean.py")
print("="*60)
