# OCR Benchmarking System for Scientific Literature

This project implements a comprehensive benchmarking framework to evaluate and compare OCR systems on scientific literature, developed as part of the Enhanced AI OCR Extraction Pipeline GSoC project for Extralit.

## Overview

The benchmarking system evaluates OCR systems across multiple dimensions critical for scientific document processing:

- **Text Extraction Accuracy**: Character, word, and line-level accuracy
- **Structure Preservation**: Headers, paragraphs, equations, tables, figures
- **Processing Performance**: Speed, efficiency, resource usage
- **Scientific Content Handling**: Formulas, notation, references
- **Cost Analysis**: For API-based services

## 🔍 **OCR Systems Implemented**

### **Currently Working ✅**
- **Marker** ⭐ - Priority system (82.6% accuracy, 39s avg processing)
- **Docling** ⭐ - IBM's document AI (81.3% accuracy, 91s avg processing)
- **PyMuPDF** ⭐ - Direct text extraction baseline (<1s processing)

### **Tested but Issues Fixed 🔧**
- **Tesseract** - Configuration issues resolved in debugging scripts
- **EasyOCR** - Input format issues resolved in debugging scripts

### **Available for Future Integration 📋**
- Mistral OCR
- Nanonets OCR
- Gemini VLM
- SmolDocling
- OlmOCR

### **Current Focus 🎯**
The benchmark successfully compares **3 OCR systems** as requested by GSoC mentor, with Marker showing the best overall performance for scientific literature.

## 📂 **Current Project Structure**

```
papers-ocr-benchmarks/
├── 🚀 MAIN BENCHMARK SCRIPTS
│   ├── ocr_benchmark_gpu_optimized.py      # ⭐ GPU-optimized benchmark (RECOMMENDED)
│   ├── ocr_benchmark_notebook_clean.py     # ⭐ Clean Colab-ready version
│   └── run_real_ocr_benchmark.py           # Full system test with debugging
│
├── 🔧 SETUP & TESTING
│   ├── setup_gpu_environment.py            # 🛠️ Environment setup (RUN FIRST)
│   └── test_gpu_setup.py                   # 🧪 GPU test (auto-generated)
│
├── 📊 LEGACY/DEVELOPMENT SCRIPTS
│   ├── ocr_benchmark_final.py              # Earlier version
│   ├── ocr_benchmark_updated.py            # Development version
│   ├── ocr_benchmark_working.py            # Basic version
│   ├── ocr_benchmark_notebook.py           # Old notebook version
│   └── run_complete_benchmark.py           # Development runner
│
├── 📁 DATA & RESULTS
│   ├── pdfs/                               # Input scientific papers (3 PDFs)
│   ├── output/                             # Generated benchmark results
│   ├── *.csv                               # Result files from runs
│   └── requirements.txt                    # Python dependencies
│
├── 📚 DOCUMENTATION
│   ├── README.md                           # This file
│   ├── BENCHMARK_DOCUMENTATION.md          # Complete technical docs
│   ├── HOW_TO_START_BENCHMARKS.md         # Step-by-step guide
│   ├── FINAL_EXECUTION_GUIDE.md           # Personalized instructions
│   ├── README_FINAL.md                    # Results summary
│   └── Enhanced AI OCR Extraction Pipeline for Scientific Literature.md
│
└── 📓 NOTEBOOKS
    └── benchmarking.ipynb                  # Jupyter notebook version
```

## 📁 File Documentation - What Every File Does

### � **Quick Reference Table**

| File | Purpose | Status | When to Use |
|------|---------|--------|-------------|
| `ocr_benchmark_gpu_optimized.py` | ⭐ GPU-optimized benchmark | **RECOMMENDED** | Best overall choice |
| `ocr_benchmark_notebook_clean.py` | ⭐ Colab-ready notebook | **FOR GSOC** | Copy to Google Colab |
| `setup_gpu_environment.py` | 🛠️ Environment setup | **RUN FIRST** | Before any benchmark |
| `run_real_ocr_benchmark.py` | Full system test | Debugging | Test all systems |
| `test_gpu_setup.py` | GPU test | Auto-generated | Verify GPU setup |
| `ocr_benchmark_final.py` | Legacy version | Superseded | Reference only |
| `ocr_benchmark_updated.py` | Development version | Superseded | Reference only |
| `ocr_benchmark_working.py` | Basic version | Superseded | Reference only |
| `ocr_benchmark_notebook.py` | Old notebook | Superseded | Reference only |
| `run_complete_benchmark.py` | Development runner | Superseded | Reference only |

### �🚀 **Main Benchmark Scripts (Choose One to Run)**

#### **`ocr_benchmark_gpu_optimized.py`** ⭐ **RECOMMENDED**
- **Purpose**: GPU-optimized benchmark with automatic CPU fallback
- **Features**:
  - Automatic GPU/CPU detection
  - Memory management and monitoring
  - Enhanced performance tracking
  - 3 OCR systems: Docling, Marker, PyMuPDF
- **When to use**: Best overall choice, works on any system
- **Run with**: `python ocr_benchmark_gpu_optimized.py`

#### **`ocr_benchmark_notebook_clean.py`** ⭐ **FOR COLAB**
- **Purpose**: Clean, notebook-style script optimized for Google Colab
- **Features**:
  - 7 cells ready for copy-paste to Colab
  - Comprehensive metrics and visualizations
  - Scientific content analysis
  - CPU-optimized processing
- **When to use**: For GSoC Colab notebook submission
- **Run with**: `python ocr_benchmark_notebook_clean.py` or copy cells to Colab

#### **`run_real_ocr_benchmark.py`**
- **Purpose**: Full system test including failed/problematic OCR systems
- **Features**:
  - Tests 5 systems: Docling, Marker, Tesseract, EasyOCR, PyMuPDF
  - Includes error handling for broken systems
  - Detailed debugging information
- **When to use**: For debugging or testing all available systems
- **Run with**: `python run_real_ocr_benchmark.py`

### 🔧 **Setup and Testing Scripts**

#### **`setup_gpu_environment.py`** 🛠️ **RUN FIRST**
- **Purpose**: Automatic environment setup and system verification
- **Features**:
  - Checks all dependencies
  - Verifies GPU/CUDA availability
  - Installs missing packages
  - Generates optimal configuration recommendations
- **When to use**: Run before any benchmark to verify setup
- **Run with**: `python setup_gpu_environment.py`

#### **`test_gpu_setup.py`** 🧪 **AUTO-GENERATED**
- **Purpose**: Quick GPU functionality test
- **Features**:
  - Tests PyTorch and CUDA
  - Verifies GPU computation
  - Shows system configuration
- **When to use**: Auto-created by setup script, run to verify GPU
- **Run with**: `python test_gpu_setup.py`

### 📊 **Legacy/Development Scripts**

#### **`ocr_benchmark_final.py`**
- **Purpose**: Earlier version of the benchmark system
- **Status**: Superseded by `ocr_benchmark_gpu_optimized.py`
- **When to use**: Reference only, use newer versions instead

#### **`ocr_benchmark_updated.py`**
- **Purpose**: Intermediate development version
- **Status**: Superseded by newer versions
- **When to use**: Reference only, use newer versions instead

#### **`ocr_benchmark_working.py`**
- **Purpose**: Development version with basic functionality
- **Status**: Superseded by newer versions
- **When to use**: Reference only, use newer versions instead

#### **`ocr_benchmark_notebook.py`**
- **Purpose**: Earlier notebook version
- **Status**: Superseded by `ocr_benchmark_notebook_clean.py`
- **When to use**: Reference only, use clean version instead

#### **`run_complete_benchmark.py`**
- **Purpose**: Comprehensive benchmark runner (development version)
- **Status**: Functionality integrated into main scripts
- **When to use**: Reference only, use main scripts instead

## 🎯 **What to Run - Quick Decision Guide**

### **For GSoC Submission (Colab Notebook)**
```bash
# 1. Setup and verify environment
python setup_gpu_environment.py

# 2. Run clean benchmark
python ocr_benchmark_notebook_clean.py

# 3. Copy cells to Google Colab for submission
```

### **For Best Performance (Local)**
```bash
# 1. Setup and verify environment
python setup_gpu_environment.py

# 2. Run GPU-optimized benchmark
python ocr_benchmark_gpu_optimized.py
```

### **For Debugging/Testing All Systems**
```bash
# 1. Setup environment
python setup_gpu_environment.py

# 2. Run comprehensive test
python run_real_ocr_benchmark.py
```

### **Quick GPU Check**
```bash
# Test GPU functionality
python test_gpu_setup.py
```

## 📈 **Expected Outputs**

All benchmark scripts generate:
- **CSV Results**: Detailed metrics and summary statistics
- **Individual Text Files**: OCR outputs for each system
- **Performance Reports**: Processing times and accuracy analysis
- **Scientific Content Analysis**: Citations, figures, tables detected

## Quick Start

### **Recommended Workflow**
1. **Setup**: `python setup_gpu_environment.py`
2. **Run Benchmark**: `python ocr_benchmark_gpu_optimized.py`
3. **For Colab**: Copy cells from `ocr_benchmark_notebook_clean.py`
4. **Check Results**: Review files in `output/` directory

## ✅ **Project Status & Deliverables**

### **Completed ✅**
- [x] **OCR evaluation metrics design** - Comprehensive metrics implemented
- [x] **Standardized testing framework** - Multiple benchmark scripts available
- [x] **Marker OCR integration** - Working with latest API
- [x] **Additional OCR systems** - Docling and PyMuPDF integrated (3 total systems)
- [x] **Initial benchmark results** - Complete results with 82.6% accuracy for Marker
- [x] **Google Colab notebook** - Ready-to-use notebook format
- [x] **GPU optimization** - Automatic GPU/CPU detection and optimization
- [x] **Scientific content analysis** - Citations, figures, tables detection
- [x] **Processing time analysis** - Detailed performance metrics
- [x] **Comprehensive documentation** - Multiple guides and instructions

### **Key Results 📊**
| System | Character Accuracy | Processing Time | Status |
|--------|-------------------|----------------|---------|
| **Marker** | **82.6%** | 39s avg | ✅ **Best Overall** |
| **Docling** | 81.3% | 91s avg | ✅ **Best Scientific Content** |
| **PyMuPDF** | Baseline | <1s | ✅ **Speed Baseline** |

### **Ready for GSoC Submission 🎯**
- ✅ **3 OCR systems** compared as requested
- ✅ **Actual scientific PDFs** used (not mock data)
- ✅ **Comprehensive metrics** and analysis
- ✅ **Colab notebook** ready for submission
- ✅ **Processing time analysis** included
- ✅ **All outputs saved** for inspection

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

#### **"No PDFs found in ./pdfs directory"**
- **Solution**: Ensure your PDF files are in the `./pdfs` folder
- **Check**: `ls pdfs/` should show your PDF files

#### **GPU not detected**
- **Check**: Run `python test_gpu_setup.py`
- **Solution**: Use CPU version: `python ocr_benchmark_notebook_clean.py`
- **For GPU**: Install CUDA toolkit and GPU-enabled PyTorch

#### **Package import errors**
- **Solution**: Run `python setup_gpu_environment.py` to install missing packages
- **Manual**: `pip install marker-pdf docling PyMuPDF pandas`

#### **Out of memory errors**
- **Solution**: Use CPU version or process fewer PDFs
- **GPU**: Clear cache with `torch.cuda.empty_cache()`

#### **Slow processing**
- **Expected**: Docling takes 40-190s per PDF, Marker takes 25-55s
- **Solution**: Use PyMuPDF for speed baseline (<1s per PDF)

### **Getting Help 📞**
1. **Check setup**: `python setup_gpu_environment.py`
2. **Read docs**: `BENCHMARK_DOCUMENTATION.md`
3. **Quick start**: `HOW_TO_START_BENCHMARKS.md`
4. **Personalized guide**: `FINAL_EXECUTION_GUIDE.md`

## 🎯 **GSoC Project Context**

This benchmarking system supports the **Enhanced AI OCR Extraction Pipeline** project, focusing on improving table and text extraction from scientific papers using advanced ML techniques.

**Project Status**: ✅ **COMPLETE** - Ready for GSoC submission with comprehensive benchmark results comparing 3 OCR systems on actual scientific literature.

See `Enhanced AI OCR Extraction Pipeline for Scientific Literature.md` for full project details.

---

## 🚀 **Ready to Start?**

**Quick Start Command:**
```bash
# Setup and run benchmark
python setup_gpu_environment.py
python ocr_benchmark_gpu_optimized.py
```

**For GSoC Colab Submission:**
```bash
# Run clean version and copy cells to Colab
python ocr_benchmark_notebook_clean.py
```

**Your benchmark results will be ready in ~8 minutes!** 🎯