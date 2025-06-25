# 🚀 HOW TO START OCR BENCHMARKS - Quick Start Guide

## 📋 Step-by-Step Instructions

### Step 1: Setup Your Environment
```bash
# 1. First, run the setup script to check your system
python setup_gpu_environment.py

# 2. Test your setup
python test_gpu_setup.py
```

### Step 2: Choose Your Benchmark Method

#### Option A: GPU-Optimized (Recommended if you have GPU)
```bash
python ocr_benchmark_gpu_optimized.py
```

#### Option B: Standard CPU Version
```bash
python ocr_benchmark_notebook_clean.py
```

#### Option C: Google Colab (For GSoC Submission)
1. Open Google Colab
2. Copy cells from `ocr_benchmark_gpu_optimized.py`
3. Upload your PDFs to `./pdfs` folder in Colab
4. Run cells sequentially

### Step 3: Monitor Progress
The benchmark will:
- ✅ Process each PDF with 3 OCR systems
- ✅ Save individual outputs to `output/` folder
- ✅ Generate comparison metrics
- ✅ Create summary statistics

### Step 4: Review Results
Check the generated files in `output/[timestamp]/`:
- `gpu_benchmark_results.csv` - Detailed results
- `gpu_benchmark_summary.csv` - Summary statistics
- Individual text files for each OCR system

## 🎯 Quick Commands

### For GPU Users:
```bash
# Setup and run
python setup_gpu_environment.py
python ocr_benchmark_gpu_optimized.py

# Check results
ls output/gpu_benchmark_*/
```

### For CPU Users:
```bash
# Setup and run
python setup_gpu_environment.py
python ocr_benchmark_notebook_clean.py

# Check results
ls output/clean_benchmark_*/
```

## 📊 Expected Output

### Console Output Example:
```
🚀 OCR BENCHMARK FOR SCIENTIFIC LITERATURE - GPU OPTIMIZED
======================================================================
Comparing 3 OCR Systems: Docling, Marker, PyMuPDF
Dataset: Scientific papers from ./pdfs directory
Compute Device: NVIDIA GeForce RTX 3080
======================================================================

🚀 GPU ACCELERATION ENABLED
   Device: NVIDIA GeForce RTX 3080
   CUDA Version: 11.8
   Total Memory: 10.0 GB

📚 Found 3 PDFs:
  • paper1.pdf
  • paper2.pdf
  • paper3.pdf

📖 Processing: paper1
------------------------------------------------------------
🔄 Docling...
    🔥 GPU Memory Used: 2.3 GB
    ⏱️  Time: 45.2s
    📝 Length: 61,550 chars
    💾 Saved: paper1_Docling.txt
🔄 Marker...
    🔥 GPU Memory Used: 3.1 GB
    ⏱️  Time: 38.4s
    📝 Length: 60,015 chars
    💾 Saved: paper1_Marker.txt
🔄 PyMuPDF...
    ⏱️  Time: 0.1s
    📝 Length: 52,363 chars
    💾 Saved: paper1_PyMuPDF.txt
```

### Results Files:
```
output/gpu_benchmark_20250625_180000/
├── gpu_benchmark_results.csv       # Main results
├── gpu_benchmark_summary.csv       # Summary stats
├── system_info.txt                 # System information
├── paper1_Docling.txt              # Individual outputs
├── paper1_Marker.txt
├── paper1_PyMuPDF.txt
└── ... (more files)
```

## 🔧 Troubleshooting

### If GPU Not Working:
```bash
# Check CUDA
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Use CPU version instead
python ocr_benchmark_notebook_clean.py
```

### If Missing Dependencies:
```bash
# Install all requirements
pip install torch torchvision pandas numpy matplotlib seaborn
pip install PyMuPDF textdistance marker-pdf docling
```

### If Out of Memory:
- Use CPU version: `python ocr_benchmark_notebook_clean.py`
- Process fewer PDFs at once
- Close other GPU applications

## 📈 Understanding Results

### Key Metrics:
- **Character Accuracy**: How well text is extracted (higher = better)
- **Processing Time**: Speed of extraction (lower = faster)
- **Scientific Elements**: Citations, figures, tables detected
- **GPU Memory**: Peak memory usage during processing

### Expected Performance:
| System | Accuracy | Speed | Best For |
|--------|----------|-------|----------|
| Marker | ~82-85% | Fast | Overall best |
| Docling | ~78-84% | Medium | Scientific content |
| PyMuPDF | Baseline | Very fast | Speed baseline |

## 🎯 For Your GSoC Submission

### Required Files:
1. **Benchmark Results**: `gpu_benchmark_results.csv`
2. **Summary Stats**: `gpu_benchmark_summary.csv`
3. **Individual Outputs**: Text files for inspection
4. **Colab Notebook**: Copy from `ocr_benchmark_gpu_optimized.py`

### Recommended Workflow:
1. ✅ Run local benchmark: `python ocr_benchmark_gpu_optimized.py`
2. ✅ Copy results to Google Colab for presentation
3. ✅ Create visualizations in Colab
4. ✅ Document findings with charts and analysis
5. ✅ Submit complete Colab notebook

## 🚀 Ready to Start?

### Final Checklist:
- [ ] PDFs in `./pdfs` directory
- [ ] Dependencies installed
- [ ] GPU setup verified (if using GPU)
- [ ] Sufficient disk space (5GB+)

### Start Command:
```bash
# GPU version (recommended)
python ocr_benchmark_gpu_optimized.py

# OR CPU version
python ocr_benchmark_notebook_clean.py
```

## 📞 Need Help?

1. **Check setup**: `python setup_gpu_environment.py`
2. **Test GPU**: `python test_gpu_setup.py`
3. **Read docs**: `BENCHMARK_DOCUMENTATION.md`
4. **Check console output** for error messages

**You're ready to benchmark! 🎯**

---

## 🎉 Summary

**To start benchmarking RIGHT NOW:**

```bash
# 1. Quick setup check
python setup_gpu_environment.py

# 2. Run benchmark (choose one)
python ocr_benchmark_gpu_optimized.py     # GPU version
# OR
python ocr_benchmark_notebook_clean.py    # CPU version

# 3. Check results
ls output/*/
```

**That's it! Your benchmark will run and generate all the results you need for your GSoC project.** 🚀
