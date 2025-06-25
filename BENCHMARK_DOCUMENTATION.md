# OCR Benchmark Documentation - Complete Guide

## 🎯 Overview
This documentation provides complete instructions for running the OCR benchmark for scientific literature as part of the GSoC Enhanced AI OCR Extraction Pipeline project.

## 📋 Prerequisites

### System Requirements
- **Python 3.8+**
- **8GB+ RAM** (16GB recommended for GPU)
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Storage**: 5GB+ free space for outputs

### Required Dependencies
```bash
# Core dependencies
pip install pandas numpy matplotlib seaborn
pip install PyMuPDF textdistance pathlib

# OCR Systems
pip install marker-pdf docling

# GPU Support (if available)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### GPU Setup (Optional but Recommended)
1. **Install CUDA Toolkit** (version 11.8 or 12.x)
2. **Install cuDNN** 
3. **Verify GPU availability**:
```python
import torch
print("CUDA Available:", torch.cuda.is_available())
print("GPU Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU")
```

## 📁 Project Structure
```
papers-ocr-benchmarks/
├── pdfs/                           # Input PDFs (your scientific papers)
├── output/                         # Generated benchmark results
├── ocr_benchmark_gpu_optimized.py  # Main GPU-optimized script
├── ocr_benchmark_notebook_clean.py # Clean notebook version
├── run_real_ocr_benchmark.py       # Full system test
└── BENCHMARK_DOCUMENTATION.md      # This file
```

## 🚀 How to Run Benchmarks

### Method 1: GPU-Optimized Script (Recommended)
```bash
# Navigate to project directory
cd papers-ocr-benchmarks

# Run GPU-optimized benchmark
python ocr_benchmark_gpu_optimized.py
```

**Features:**
- ✅ Automatic GPU detection and optimization
- ✅ Enhanced memory management
- ✅ GPU memory usage tracking
- ✅ Optimized for scientific literature

### Method 2: Clean Notebook Version
```bash
# For standard CPU processing
python ocr_benchmark_notebook_clean.py
```

**Features:**
- ✅ Notebook-style cells for Colab
- ✅ Clean, well-documented code
- ✅ Easy to copy-paste to Google Colab

### Method 3: Google Colab (GSoC Deliverable)

1. **Open Google Colab**
2. **Copy cells** from `ocr_benchmark_gpu_optimized.py` (marked with `#%% Cell X`)
3. **Paste each cell** into separate Colab cells
4. **Upload your PDFs** to Colab's `./pdfs` directory
5. **Run cells sequentially**

## 📊 Expected Outputs

### Directory Structure After Running
```
output/gpu_benchmark_YYYYMMDD_HHMMSS/
├── gpu_benchmark_results.csv       # Detailed per-document results
├── gpu_benchmark_summary.csv       # Summary statistics
├── system_info.txt                 # GPU/system information
├── [PDF_NAME]_Docling.txt          # Docling extraction
├── [PDF_NAME]_Marker.txt           # Marker extraction
└── [PDF_NAME]_PyMuPDF.txt          # PyMuPDF extraction
```

### Key Result Files

#### 1. `gpu_benchmark_results.csv`
Contains detailed metrics for each PDF and OCR system:
- Character/Word accuracy
- Processing time
- GPU memory usage
- Scientific elements detected
- Text length and ratios

#### 2. `gpu_benchmark_summary.csv`
Summary statistics across all documents:
- Mean accuracy scores
- Average processing times
- Standard deviations
- GPU performance metrics

#### 3. Individual Text Files
Raw OCR outputs for manual inspection and quality assessment.

## 📈 Performance Metrics Explained

### Accuracy Metrics
- **Character Accuracy**: Levenshtein distance at character level vs baseline
- **Word Accuracy**: Levenshtein distance at word level vs baseline
- **Length Ratio**: Output length compared to baseline

### Scientific Content Metrics
- **Equations**: Mathematical formulas detected
- **Citations**: Reference citations found
- **Figures**: Figure references identified
- **Tables**: Table references found
- **Formulas**: Mathematical expressions

### Performance Metrics
- **Processing Time**: Time taken per document
- **GPU Memory Used**: Peak GPU memory consumption
- **Device**: CPU vs GPU processing

## 🔧 Troubleshooting

### Common Issues

#### 1. GPU Not Detected
```bash
# Check CUDA installation
nvidia-smi

# Verify PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

**Solutions:**
- Install/reinstall CUDA toolkit
- Install correct PyTorch version for your CUDA
- Check GPU drivers

#### 2. Out of Memory Errors
**Symptoms:** CUDA out of memory, system freezing

**Solutions:**
- Reduce batch size in DataLoader
- Process fewer documents at once
- Clear GPU cache: `torch.cuda.empty_cache()`
- Use CPU mode if GPU memory insufficient

#### 3. Missing Dependencies
```bash
# Install missing packages
pip install -r requirements.txt

# For specific OCR systems
pip install marker-pdf docling pytesseract
```

#### 4. PDF Loading Errors
**Check:**
- PDFs are in `./pdfs` directory
- PDFs are not corrupted
- Sufficient disk space

### Performance Optimization

#### For GPU Systems
```python
# Optimal settings (already included in gpu_optimized script)
torch.backends.cudnn.benchmark = True
torch.cuda.empty_cache()
pin_memory = torch.cuda.is_available()
```

#### For CPU Systems
- Use the clean notebook version
- Process documents sequentially
- Monitor RAM usage

## 📋 Benchmark Execution Checklist

### Pre-Execution
- [ ] GPU drivers installed and working
- [ ] CUDA toolkit installed (if using GPU)
- [ ] All dependencies installed
- [ ] PDFs placed in `./pdfs` directory
- [ ] Sufficient disk space (5GB+)

### During Execution
- [ ] Monitor GPU/CPU usage
- [ ] Check for error messages
- [ ] Verify output files are being created
- [ ] Monitor processing times

### Post-Execution
- [ ] Review benchmark results CSV
- [ ] Check individual OCR outputs
- [ ] Verify all PDFs were processed
- [ ] Compare accuracy metrics
- [ ] Document findings for GSoC

## 🎯 For GSoC Submission

### Required Deliverables
1. **Benchmark Results**: CSV files with metrics
2. **Colab Notebook**: Copy cells from GPU-optimized script
3. **Analysis**: Performance comparison of 3 OCR systems
4. **Documentation**: This guide + results interpretation

### Recommended Workflow
1. **Run GPU-optimized benchmark** locally
2. **Copy results** to Google Colab for presentation
3. **Create visualizations** in Colab
4. **Document findings** with metrics and charts
5. **Submit** Colab notebook with complete analysis

## 🔍 Results Interpretation

### Expected Performance (Based on Previous Runs)
| System | Character Accuracy | Processing Time | Best For |
|--------|-------------------|----------------|----------|
| **Marker** | ~82-85% | 25-55s | Best overall accuracy |
| **Docling** | ~78-84% | 40-190s | Scientific content |
| **PyMuPDF** | Baseline | <1s | Speed baseline |

### Key Insights
- **Marker**: Best balance of accuracy and speed
- **Docling**: Excellent for complex scientific documents
- **GPU Acceleration**: 2-5x speedup for AI-based systems
- **Scientific Content**: All systems preserve basic structure

## 🚀 Quick Start Commands

```bash
# 1. Setup environment
pip install torch torchvision marker-pdf docling pandas matplotlib

# 2. Verify GPU (optional)
python -c "import torch; print('GPU:', torch.cuda.is_available())"

# 3. Run benchmark
python ocr_benchmark_gpu_optimized.py

# 4. Check results
ls output/gpu_benchmark_*/
```

## 📞 Support
For issues or questions:
1. Check this documentation
2. Review error messages in console output
3. Verify system requirements
4. Check GPU/CUDA installation if using GPU mode

**Ready to benchmark! 🎯**
