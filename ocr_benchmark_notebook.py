# OCR Benchmarking System for Scientific Literature
# GSoC Project: Enhanced AI OCR Extraction Pipeline for Extralit
# Author: Priyankesh
# 
# This script is designed to be copied cell-by-cell into a Google Colab notebook
# Each cell is marked with #cell X comments

#cell 1 - Setup and Imports
"""
OCR Benchmarking Framework Setup
Install required packages and import necessary libraries
"""

# Install required packages (uncomment in Colab)
# !pip install marker-pdf pymupdf opencv-python pandas numpy matplotlib seaborn
# !pip install textdistance nltk scikit-learn pillow
# !pip install google-generativeai  # for Gemini VLM
# !pip install requests  # for API calls

import os
import time
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import cv2
import fitz  # PyMuPDF
from PIL import Image
import textdistance
import nltk
from sklearn.metrics import accuracy_score
import re
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

print("✅ Setup complete!")

#cell 2 - Define Evaluation Metrics
"""
Comprehensive OCR Evaluation Metrics for Scientific Documents
"""

class OCRMetrics:
    """
    Comprehensive metrics for evaluating OCR performance on scientific documents
    """
    
    def __init__(self):
        self.results = {}
    
    def character_accuracy(self, ground_truth: str, predicted: str) -> float:
        """Character-level accuracy using edit distance"""
        if not ground_truth or not predicted:
            return 0.0
        
        # Normalize whitespace
        gt_clean = re.sub(r'\s+', ' ', ground_truth.strip())
        pred_clean = re.sub(r'\s+', ' ', predicted.strip())
        
        # Calculate character-level accuracy
        distance = textdistance.levenshtein(gt_clean, pred_clean)
        max_len = max(len(gt_clean), len(pred_clean))
        
        if max_len == 0:
            return 1.0
        
        accuracy = 1 - (distance / max_len)
        return max(0.0, accuracy)
    
    def word_accuracy(self, ground_truth: str, predicted: str) -> float:
        """Word-level accuracy"""
        if not ground_truth or not predicted:
            return 0.0
            
        gt_words = ground_truth.lower().split()
        pred_words = predicted.lower().split()
        
        if not gt_words:
            return 1.0 if not pred_words else 0.0
        
        # Calculate word-level edit distance
        distance = textdistance.levenshtein(gt_words, pred_words)
        accuracy = 1 - (distance / max(len(gt_words), len(pred_words)))
        return max(0.0, accuracy)
    
    def scientific_notation_accuracy(self, ground_truth: str, predicted: str) -> float:
        """Accuracy for scientific notation, formulas, and special characters"""
        # Patterns for scientific content
        patterns = [
            r'\d+\.\d+[eE][+-]?\d+',  # Scientific notation
            r'[α-ωΑ-Ω]',              # Greek letters
            r'[₀-₉⁰-⁹]',              # Subscripts/superscripts
            r'[±×÷≤≥≠≈∞∑∏∫]',         # Mathematical symbols
            r'\$[^$]+\$',             # LaTeX math
        ]
        
        gt_matches = []
        pred_matches = []
        
        for pattern in patterns:
            gt_matches.extend(re.findall(pattern, ground_truth))
            pred_matches.extend(re.findall(pattern, predicted))
        
        if not gt_matches:
            return 1.0 if not pred_matches else 0.0
        
        # Calculate accuracy for scientific notation
        correct = len(set(gt_matches) & set(pred_matches))
        total = len(set(gt_matches))
        
        return correct / total if total > 0 else 1.0
    
    def structure_preservation_score(self, ground_truth: str, predicted: str) -> Dict[str, float]:
        """Evaluate preservation of document structure"""
        scores = {}
        
        # Header detection (lines with fewer words, often capitalized)
        gt_headers = self._detect_headers(ground_truth)
        pred_headers = self._detect_headers(predicted)
        scores['headers'] = self._calculate_overlap(gt_headers, pred_headers)
        
        # Paragraph detection (separated by double newlines)
        gt_paragraphs = len(re.split(r'\n\s*\n', ground_truth.strip()))
        pred_paragraphs = len(re.split(r'\n\s*\n', predicted.strip()))
        scores['paragraphs'] = 1 - abs(gt_paragraphs - pred_paragraphs) / max(gt_paragraphs, 1)
        
        # List detection (lines starting with numbers or bullets)
        gt_lists = len(re.findall(r'^\s*[\d\-\*\•]\s+', ground_truth, re.MULTILINE))
        pred_lists = len(re.findall(r'^\s*[\d\-\*\•]\s+', predicted, re.MULTILINE))
        scores['lists'] = 1 - abs(gt_lists - pred_lists) / max(gt_lists, 1) if gt_lists > 0 else 1.0
        
        return scores
    
    def _detect_headers(self, text: str) -> List[str]:
        """Simple header detection heuristic"""
        lines = text.split('\n')
        headers = []
        
        for line in lines:
            line = line.strip()
            if (len(line) > 0 and len(line.split()) <= 8 and 
                (line.isupper() or line.istitle()) and 
                not line.endswith('.')):
                headers.append(line.lower())
        
        return headers
    
    def _calculate_overlap(self, list1: List[str], list2: List[str]) -> float:
        """Calculate overlap between two lists"""
        if not list1:
            return 1.0 if not list2 else 0.0
        
        set1, set2 = set(list1), set(list2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 1.0

print("✅ Metrics defined!")

#cell 3 - OCR System Implementations
"""
OCR System Integrations
Starting with Marker (required) and PyMuPDF+OpenCV
"""

class OCRSystem:
    """Base class for OCR systems"""
    
    def __init__(self, name: str):
        self.name = name
    
    def extract_text(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract text from PDF
        Returns: (extracted_text, metadata)
        """
        raise NotImplementedError
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {}

class MarkerOCR(OCRSystem):
    """Marker OCR System Integration"""
    
    def __init__(self):
        super().__init__("Marker")
        self.processing_time = 0
        self.memory_usage = 0
    
    def extract_text(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text using Marker"""
        start_time = time.time()
        
        try:
            # Note: This is a placeholder - actual Marker integration would go here
            # For now, we'll simulate Marker's output
            print(f"🔄 Processing {pdf_path} with Marker...")
            
            # Simulate processing time
            time.sleep(2)
            
            # Placeholder text extraction (replace with actual Marker call)
            extracted_text = f"[MARKER SIMULATION] Extracted text from {os.path.basename(pdf_path)}"
            
            self.processing_time = time.time() - start_time
            
            metadata = {
                'processing_time': self.processing_time,
                'pages_processed': 1,  # Would be actual page count
                'confidence_score': 0.95,  # Marker's confidence if available
                'status': 'success'
            }
            
            return extracted_text, metadata
            
        except Exception as e:
            self.processing_time = time.time() - start_time
            return f"Error: {str(e)}", {'status': 'error', 'processing_time': self.processing_time}

class PyMuPDFOCR(OCRSystem):
    """PyMuPDF + OpenCV OCR System"""
    
    def __init__(self):
        super().__init__("PyMuPDF+OpenCV")
        self.processing_time = 0
    
    def extract_text(self, pdf_path: str) -> Tuple[str, Dict[str, Any]]:
        """Extract text using PyMuPDF with OpenCV preprocessing"""
        start_time = time.time()
        
        try:
            print(f"🔄 Processing {pdf_path} with PyMuPDF+OpenCV...")
            
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            extracted_text = ""
            pages_processed = 0
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # First try direct text extraction
                text = page.get_text()
                
                if len(text.strip()) < 50:  # If little text found, use OCR
                    # Convert page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
                    img_data = pix.tobytes("png")
                    
                    # Convert to OpenCV format
                    nparr = np.frombuffer(img_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    # Basic image preprocessing
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # Apply threshold to get binary image
                    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
                    # For actual OCR, you'd use pytesseract here
                    # text = pytesseract.image_to_string(binary)
                    text = f"[OCR SIMULATION] Page {page_num + 1} content from {os.path.basename(pdf_path)}"
                
                extracted_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
                pages_processed += 1
            
            doc.close()
            
            self.processing_time = time.time() - start_time
            
            metadata = {
                'processing_time': self.processing_time,
                'pages_processed': pages_processed,
                'method': 'hybrid_text_ocr',
                'status': 'success'
            }
            
            return extracted_text, metadata
            
        except Exception as e:
            self.processing_time = time.time() - start_time
            return f"Error: {str(e)}", {'status': 'error', 'processing_time': self.processing_time}

# Initialize OCR systems
ocr_systems = {
    'marker': MarkerOCR(),
    'pymupdf_opencv': PyMuPDFOCR()
}

print("✅ OCR systems initialized!")
print(f"Available systems: {list(ocr_systems.keys())}")

#cell 4 - Dataset Preparation and Ground Truth
"""
Prepare dataset and create ground truth for evaluation
"""

class DatasetManager:
    """Manage scientific papers dataset and ground truth"""

    def __init__(self, pdf_directory: str = "./pdfs"):
        self.pdf_directory = Path(pdf_directory)
        self.ground_truth = {}
        self.papers = []

    def load_papers(self) -> List[str]:
        """Load available PDF papers"""
        if not self.pdf_directory.exists():
            print(f"❌ PDF directory {self.pdf_directory} not found!")
            return []

        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        self.papers = [str(pdf) for pdf in pdf_files]

        print(f"📚 Found {len(self.papers)} papers:")
        for i, paper in enumerate(self.papers, 1):
            print(f"  {i}. {Path(paper).name}")

        return self.papers

    def create_sample_ground_truth(self):
        """
        Create sample ground truth for evaluation
        In a real scenario, this would be manually annotated or extracted from clean sources
        """
        # Sample ground truth for demonstration
        # In practice, you'd have actual ground truth text for each paper

        sample_texts = {
            "2014-Combining_organophosphate_treated_wall_linings_and_long-lasting_insecticidal_nets_for_improved_control_of_pyrethroi.pdf": {
                "title": "Combining organophosphate treated wall linings and long-lasting insecticidal nets for improved control of pyrethroid resistant Anopheles gambiae",
                "abstract": "Background: Insecticide resistance in malaria vectors threatens the continued effectiveness of vector control interventions...",
                "key_findings": "The combination of organophosphate treated wall linings with LLINs showed significant improvement in mosquito control.",
                "sample_text": """
                ABSTRACT

                Background: Insecticide resistance in malaria vectors threatens the continued effectiveness of vector control interventions. Novel approaches are needed to manage resistance and maintain the gains achieved in malaria control.

                Methods: We evaluated the efficacy of combining organophosphate-treated wall linings with long-lasting insecticidal nets (LLINs) against pyrethroid-resistant Anopheles gambiae in experimental huts.

                Results: The combination treatment showed significantly higher mortality rates (85.2%) compared to LLINs alone (45.3%) or wall linings alone (62.1%). Blood feeding rates were reduced by 78% with the combination treatment.

                Conclusions: Combining organophosphate wall linings with LLINs provides enhanced control of pyrethroid-resistant malaria vectors and represents a promising resistance management strategy.
                """
            },

            "Allossogbe_et_al_2017_Mal_J.pdf": {
                "title": "Malaria vector control in Benin: efficacy of pyrethroid-treated nets",
                "sample_text": """
                INTRODUCTION

                Malaria remains a major public health challenge in sub-Saharan Africa. Vector control using insecticide-treated nets (ITNs) has been a cornerstone of malaria prevention strategies.

                METHODS

                We conducted a randomized controlled trial in rural Benin to evaluate the effectiveness of pyrethroid-treated nets. Study participants (n=2,450) were randomly allocated to intervention and control groups.

                RESULTS

                The intervention group showed a 42% reduction in malaria incidence (95% CI: 28-54%, p<0.001). Entomological surveys revealed significant reductions in vector density and sporozoite rates.
                """
            },

            "Somboon_et_al_1995_Trans_RSTMH.pdf": {
                "title": "Anopheles dirus and malaria transmission in Thailand",
                "sample_text": """
                SUMMARY

                Anopheles dirus is the primary malaria vector in forested areas of Southeast Asia. This study examined the bionomics and vectorial capacity of An. dirus populations in Thailand.

                Field collections were conducted in three provinces over 24 months. Mosquitoes were identified morphologically and tested for Plasmodium infection using ELISA.

                A total of 3,247 An. dirus were collected. Sporozoite rates ranged from 2.1% to 8.7% across sites. Peak biting activity occurred between 22:00 and 02:00 hours.

                The study confirms An. dirus as an efficient malaria vector with high anthropophilic behavior and significant epidemiological importance in forest-fringe communities.
                """
            }
        }

        self.ground_truth = sample_texts
        print("✅ Sample ground truth created!")
        print(f"Ground truth available for {len(self.ground_truth)} papers")

        return self.ground_truth

    def get_ground_truth(self, paper_name: str) -> str:
        """Get ground truth text for a specific paper"""
        paper_basename = Path(paper_name).name
        if paper_basename in self.ground_truth:
            return self.ground_truth[paper_basename]["sample_text"]
        return ""

# Initialize dataset manager
dataset = DatasetManager()
papers = dataset.load_papers()
ground_truth = dataset.create_sample_ground_truth()

#cell 5 - Benchmarking Framework
"""
Core benchmarking framework to run OCR systems and collect metrics
"""

class OCRBenchmark:
    """Main benchmarking framework"""

    def __init__(self, ocr_systems: Dict, dataset_manager: DatasetManager, metrics: OCRMetrics):
        self.ocr_systems = ocr_systems
        self.dataset = dataset_manager
        self.metrics = metrics
        self.results = {}

    def run_benchmark(self, systems_to_test: List[str] = None) -> Dict:
        """Run benchmark on specified OCR systems"""

        if systems_to_test is None:
            systems_to_test = list(self.ocr_systems.keys())

        print(f"🚀 Starting OCR benchmark...")
        print(f"Systems to test: {systems_to_test}")
        print(f"Papers to process: {len(self.dataset.papers)}")
        print("-" * 50)

        for system_name in systems_to_test:
            if system_name not in self.ocr_systems:
                print(f"❌ System '{system_name}' not found!")
                continue

            print(f"\n📊 Testing {system_name.upper()}...")
            system = self.ocr_systems[system_name]
            system_results = []

            for paper_path in self.dataset.papers:
                paper_name = Path(paper_path).name
                print(f"  Processing: {paper_name}")

                # Extract text using OCR system
                extracted_text, metadata = system.extract_text(paper_path)

                # Get ground truth
                ground_truth_text = self.dataset.get_ground_truth(paper_path)

                # Calculate metrics
                if ground_truth_text and "Error:" not in extracted_text:
                    char_acc = self.metrics.character_accuracy(ground_truth_text, extracted_text)
                    word_acc = self.metrics.word_accuracy(ground_truth_text, extracted_text)
                    sci_acc = self.metrics.scientific_notation_accuracy(ground_truth_text, extracted_text)
                    struct_scores = self.metrics.structure_preservation_score(ground_truth_text, extracted_text)

                    paper_result = {
                        'paper': paper_name,
                        'system': system_name,
                        'character_accuracy': char_acc,
                        'word_accuracy': word_acc,
                        'scientific_accuracy': sci_acc,
                        'structure_scores': struct_scores,
                        'processing_time': metadata.get('processing_time', 0),
                        'pages_processed': metadata.get('pages_processed', 0),
                        'status': metadata.get('status', 'unknown'),
                        'extracted_length': len(extracted_text),
                        'ground_truth_length': len(ground_truth_text)
                    }
                else:
                    paper_result = {
                        'paper': paper_name,
                        'system': system_name,
                        'character_accuracy': 0.0,
                        'word_accuracy': 0.0,
                        'scientific_accuracy': 0.0,
                        'structure_scores': {'headers': 0, 'paragraphs': 0, 'lists': 0},
                        'processing_time': metadata.get('processing_time', 0),
                        'pages_processed': metadata.get('pages_processed', 0),
                        'status': 'error' if "Error:" in extracted_text else 'no_ground_truth',
                        'extracted_length': len(extracted_text),
                        'ground_truth_length': len(ground_truth_text)
                    }

                system_results.append(paper_result)

                # Print quick summary
                if paper_result['status'] == 'success' or 'accuracy' in paper_result:
                    print(f"    ✅ Char: {paper_result['character_accuracy']:.2f}, "
                          f"Word: {paper_result['word_accuracy']:.2f}, "
                          f"Time: {paper_result['processing_time']:.2f}s")
                else:
                    print(f"    ❌ {paper_result['status']}")

            self.results[system_name] = system_results

        print("\n✅ Benchmark completed!")
        return self.results

    def get_summary_stats(self) -> pd.DataFrame:
        """Generate summary statistics"""
        summary_data = []

        for system_name, results in self.results.items():
            if not results:
                continue

            # Calculate averages
            char_accs = [r['character_accuracy'] for r in results if r['status'] != 'error']
            word_accs = [r['word_accuracy'] for r in results if r['status'] != 'error']
            sci_accs = [r['scientific_accuracy'] for r in results if r['status'] != 'error']
            proc_times = [r['processing_time'] for r in results]

            # Structure scores
            header_scores = [r['structure_scores']['headers'] for r in results if r['status'] != 'error']
            para_scores = [r['structure_scores']['paragraphs'] for r in results if r['status'] != 'error']
            list_scores = [r['structure_scores']['lists'] for r in results if r['status'] != 'error']

            summary_data.append({
                'System': system_name,
                'Avg_Character_Accuracy': np.mean(char_accs) if char_accs else 0,
                'Avg_Word_Accuracy': np.mean(word_accs) if word_accs else 0,
                'Avg_Scientific_Accuracy': np.mean(sci_accs) if sci_accs else 0,
                'Avg_Header_Preservation': np.mean(header_scores) if header_scores else 0,
                'Avg_Paragraph_Preservation': np.mean(para_scores) if para_scores else 0,
                'Avg_List_Preservation': np.mean(list_scores) if list_scores else 0,
                'Avg_Processing_Time': np.mean(proc_times) if proc_times else 0,
                'Total_Papers_Processed': len([r for r in results if r['status'] != 'error']),
                'Success_Rate': len([r for r in results if r['status'] != 'error']) / len(results) if results else 0
            })

        return pd.DataFrame(summary_data)

# Initialize benchmark
benchmark = OCRBenchmark(ocr_systems, dataset, OCRMetrics())

print("✅ Benchmarking framework ready!")

#cell 6 - Run the Benchmark
"""
Execute the benchmark on available OCR systems
"""

# Run benchmark on Marker and PyMuPDF+OpenCV (as requested: 3 systems minimum)
print("🎯 Running OCR Benchmark - Initial Results")
print("=" * 60)

# Test systems (Marker + 1 other for initial deliverable)
test_systems = ['marker', 'pymupdf_opencv']

# Execute benchmark
results = benchmark.run_benchmark(test_systems)

# Generate summary statistics
summary_df = benchmark.get_summary_stats()

print("\n📊 BENCHMARK SUMMARY")
print("=" * 60)
print(summary_df.round(3))

#cell 7 - Detailed Results Analysis
"""
Analyze and visualize benchmark results
"""

# Convert results to DataFrame for easier analysis
detailed_results = []
for system_name, system_results in results.items():
    for result in system_results:
        row = result.copy()
        # Flatten structure scores
        if 'structure_scores' in row:
            for key, value in row['structure_scores'].items():
                row[f'structure_{key}'] = value
            del row['structure_scores']
        detailed_results.append(row)

results_df = pd.DataFrame(detailed_results)

print("📈 DETAILED RESULTS ANALYSIS")
print("=" * 50)

if not results_df.empty:
    print("\n1. ACCURACY METRICS BY SYSTEM:")
    accuracy_summary = results_df.groupby('system')[
        ['character_accuracy', 'word_accuracy', 'scientific_accuracy']
    ].agg(['mean', 'std']).round(3)
    print(accuracy_summary)

    print("\n2. PROCESSING PERFORMANCE:")
    performance_summary = results_df.groupby('system')[
        ['processing_time', 'pages_processed']
    ].agg(['mean', 'sum']).round(3)
    print(performance_summary)

    print("\n3. STRUCTURE PRESERVATION:")
    structure_summary = results_df.groupby('system')[
        ['structure_headers', 'structure_paragraphs', 'structure_lists']
    ].mean().round(3)
    print(structure_summary)

    print("\n4. SUCCESS RATES:")
    success_rates = results_df.groupby('system')['status'].apply(
        lambda x: (x != 'error').mean()
    ).round(3)
    print(success_rates)

else:
    print("❌ No results to analyze!")

#cell 8 - Visualization
"""
Create visualizations for benchmark results
"""

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

if not results_df.empty and len(results_df) > 0:

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('OCR Systems Benchmark Results - Scientific Literature', fontsize=16, fontweight='bold')

    # 1. Accuracy Comparison
    accuracy_data = results_df.groupby('system')[
        ['character_accuracy', 'word_accuracy', 'scientific_accuracy']
    ].mean()

    accuracy_data.plot(kind='bar', ax=axes[0,0], rot=45)
    axes[0,0].set_title('Accuracy Metrics Comparison')
    axes[0,0].set_ylabel('Accuracy Score')
    axes[0,0].legend(['Character', 'Word', 'Scientific'])
    axes[0,0].grid(True, alpha=0.3)

    # 2. Processing Time
    proc_time_data = results_df.groupby('system')['processing_time'].mean()
    proc_time_data.plot(kind='bar', ax=axes[0,1], color='orange', rot=45)
    axes[0,1].set_title('Average Processing Time')
    axes[0,1].set_ylabel('Time (seconds)')
    axes[0,1].grid(True, alpha=0.3)

    # 3. Structure Preservation
    structure_data = results_df.groupby('system')[
        ['structure_headers', 'structure_paragraphs', 'structure_lists']
    ].mean()

    structure_data.plot(kind='bar', ax=axes[1,0], rot=45)
    axes[1,0].set_title('Structure Preservation Scores')
    axes[1,0].set_ylabel('Preservation Score')
    axes[1,0].legend(['Headers', 'Paragraphs', 'Lists'])
    axes[1,0].grid(True, alpha=0.3)

    # 4. Overall Performance Radar (simplified)
    systems = results_df['system'].unique()
    metrics = ['character_accuracy', 'word_accuracy', 'scientific_accuracy', 'processing_time']

    # Normalize processing time (invert so higher is better)
    results_df_norm = results_df.copy()
    max_time = results_df_norm['processing_time'].max()
    results_df_norm['processing_time'] = 1 - (results_df_norm['processing_time'] / max_time)

    overall_scores = results_df_norm.groupby('system')[metrics].mean()
    overall_scores.plot(kind='bar', ax=axes[1,1], rot=45)
    axes[1,1].set_title('Overall Performance (Normalized)')
    axes[1,1].set_ylabel('Normalized Score')
    axes[1,1].legend(['Char Acc', 'Word Acc', 'Sci Acc', 'Speed'])
    axes[1,1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Additional detailed plot: Per-paper performance
    if len(results_df) > 2:
        fig2, ax2 = plt.subplots(1, 1, figsize=(12, 6))

        # Character accuracy by paper and system
        pivot_data = results_df.pivot(index='paper', columns='system', values='character_accuracy')
        pivot_data.plot(kind='bar', ax=ax2, rot=45)
        ax2.set_title('Character Accuracy by Paper and OCR System')
        ax2.set_ylabel('Character Accuracy')
        ax2.legend(title='OCR System')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

else:
    print("❌ No data available for visualization!")

#cell 9 - Cost Analysis (Placeholder)
"""
Cost analysis for API-based OCR services
"""

print("💰 COST ANALYSIS")
print("=" * 40)

# Placeholder cost analysis
# In practice, you'd track actual API costs
cost_estimates = {
    'marker': {
        'cost_per_page': 0.01,  # Estimated
        'setup_cost': 0.0,
        'description': 'Open-source, self-hosted'
    },
    'pymupdf_opencv': {
        'cost_per_page': 0.0,
        'setup_cost': 0.0,
        'description': 'Free, open-source'
    },
    'gemini_vlm': {
        'cost_per_page': 0.05,  # Estimated API cost
        'setup_cost': 0.0,
        'description': 'Google API pricing'
    },
    'nanonets': {
        'cost_per_page': 0.02,
        'setup_cost': 0.0,
        'description': 'Commercial API'
    }
}

if not results_df.empty:
    total_pages = results_df['pages_processed'].sum()

    print(f"Total pages processed: {total_pages}")
    print("\nEstimated costs per system:")

    for system, costs in cost_estimates.items():
        if system in results_df['system'].values:
            system_pages = results_df[results_df['system'] == system]['pages_processed'].sum()
            estimated_cost = system_pages * costs['cost_per_page'] + costs['setup_cost']
            print(f"  {system}: ${estimated_cost:.2f} ({costs['description']})")

#cell 10 - Export Results and Summary
"""
Export results and create summary for Colab notebook
"""

print("📤 EXPORTING RESULTS")
print("=" * 30)

# Save detailed results
if not results_df.empty:
    results_df.to_csv('ocr_benchmark_results.csv', index=False)
    print("✅ Detailed results saved to: ocr_benchmark_results.csv")

# Save summary
summary_df.to_csv('ocr_benchmark_summary.csv', index=False)
print("✅ Summary saved to: ocr_benchmark_summary.csv")

# Create final summary report
print("\n" + "="*60)
print("🎯 FINAL BENCHMARK REPORT")
print("="*60)

print(f"\n📊 SYSTEMS TESTED: {len(test_systems)}")
for system in test_systems:
    print(f"  • {system}")

print(f"\n📚 PAPERS PROCESSED: {len(papers)}")
for paper in papers:
    print(f"  • {Path(paper).name}")

if not summary_df.empty:
    print(f"\n🏆 TOP PERFORMER BY METRIC:")

    metrics_to_check = [
        ('Character Accuracy', 'Avg_Character_Accuracy'),
        ('Word Accuracy', 'Avg_Word_Accuracy'),
        ('Scientific Accuracy', 'Avg_Scientific_Accuracy'),
        ('Processing Speed', 'Avg_Processing_Time')  # Lower is better
    ]

    for metric_name, column in metrics_to_check:
        if column in summary_df.columns:
            if 'Time' in metric_name:
                best_system = summary_df.loc[summary_df[column].idxmin(), 'System']
                best_value = summary_df[column].min()
            else:
                best_system = summary_df.loc[summary_df[column].idxmax(), 'System']
                best_value = summary_df[column].max()
            print(f"  • {metric_name}: {best_system} ({best_value:.3f})")

print(f"\n⏱️  TOTAL PROCESSING TIME: {results_df['processing_time'].sum():.2f} seconds")
print(f"📄 TOTAL PAGES PROCESSED: {results_df['pages_processed'].sum()}")

print("\n" + "="*60)
print("✅ BENCHMARK COMPLETE!")
print("="*60)

print("""
🚀 NEXT STEPS:
1. Add more OCR systems (Gemini VLM, Mistral OCR, etc.)
2. Expand dataset with more scientific papers
3. Create manual ground truth annotations
4. Implement table-specific evaluation metrics
5. Add figure/equation extraction evaluation
6. Deploy as automated benchmarking pipeline

📝 FOR COLAB NOTEBOOK:
- Copy each cell above into separate Colab cells
- Install required packages in first cell
- Upload PDF files to Colab environment
- Run cells sequentially
- Download results CSV files
""")
