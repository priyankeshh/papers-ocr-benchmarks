# OCR Benchmark Execution Guide

## 🚀 **WHICH FILE TO RUN**

### **Option 1: Real OCR Systems (RECOMMENDED)**
```bash
python run_real_ocr_benchmark.py
```
**What it does:**
- Uses actual Docling, Marker, Tesseract when available
- Falls back gracefully if libraries aren't installed
- Saves all extracted texts to organized folders
- Shows real processing times and comparisons

### **Option 2: Simulation Mode**
```bash
python run_complete_benchmark.py
```
**What it does:**
- Simulates different OCR approaches using PyMuPDF
- Always works regardless of installed libraries
- Good for testing the framework structure
- Shows how different processing methods affect output

### **Option 3: Framework Only (No Execution)**
```bash
python ocr_benchmark_updated.py
```
**What it does:**
- Only loads the classes and functions
- Doesn't actually run any benchmark
- Just shows "Setup complete!" message

---

## 📁 **OUTPUT STRUCTURE**

When you run the benchmark, it creates:

```
./output/
└── real_ocr_benchmark_YYYYMMDD_HHMMSS/
    ├── extracted_texts/          # Raw OCR outputs
    │   ├── paper1_Docling.txt
    │   ├── paper1_Marker.txt
    │   ├── paper1_PyMuPDF.txt
    │   └── paper1_Tesseract.txt
    ├── summaries/                 # Results & analysis
    │   ├── real_benchmark_results.csv
    │   └── real_benchmark_summary.csv
    └── comparisons/               # (Future: side-by-side comparisons)
```

---

## 🔍 **WHAT YOU'LL SEE**

### **During Execution:**
```
🚀 REAL OCR BENCHMARK
============================================================
✅ Docling available
✅ Marker available  
⚠️  Tesseract not available
✅ PyMuPDF available

🔧 Initialized 3 OCR systems:
  • Docling
  • Marker
  • PyMuPDF

📚 Found 3 PDFs:
  • 2014-Combining_organophosphate_treated_wall_linings...
  • Allossogbe_et_al_2017_Mal_J
  • Somboon_et_al_1995_Trans_RSTMH

📖 Processing: 2014-Combining_organophosphate_treated_wall_linings...
--------------------------------------------------
🔄 Docling...
  🔄 Processing with Docling...
    💾 Saved: 2014-Combining_organophosphate_treated_wall_linings_Docling.txt (61550 chars)
    ⏱️  Time: 124.55s

🔄 Marker...
  🔄 Processing with Marker...
    💾 Saved: 2014-Combining_organophosphate_treated_wall_linings_Marker.txt (45230 chars)
    ⏱️  Time: 89.23s

🔄 PyMuPDF...
  🔄 Processing with PyMuPDF...
    💾 Saved: 2014-Combining_organophosphate_treated_wall_linings_PyMuPDF.txt (38920 chars)
    ⏱️  Time: 2.15s
```

### **Final Results:**
```
📊 BENCHMARK SUMMARY
============================================================
                Character_Accuracy  Word_Accuracy  Length_Ratio  Processing_Time  Text_Length
System
Docling                      0.923          0.891         1.580           124.550     61550.0
Marker                       0.887          0.845         1.163            89.230     45230.0
Tesseract                    0.756          0.723         0.892            15.670     34720.0
```

---

## 📄 **EXAMINING THE OUTPUTS**

### **1. Check Extracted Texts**
```bash
# Look at what each system extracted
cat ./output/real_ocr_benchmark_*/extracted_texts/paper1_Docling.txt
cat ./output/real_ocr_benchmark_*/extracted_texts/paper1_Marker.txt
```

### **2. Compare Results**
```bash
# Open the CSV files in Excel or view in terminal
cat ./output/real_ocr_benchmark_*/summaries/real_benchmark_summary.csv
```

### **3. Analyze Processing Times**
The CSV files show:
- **Character_Accuracy**: How similar the text is to baseline
- **Word_Accuracy**: Word-level comparison
- **Length_Ratio**: How much text was extracted (>1 = more, <1 = less)
- **Processing_Time**: Seconds to process each PDF
- **Text_Length**: Total characters extracted

---

## 🔧 **TROUBLESHOOTING**

### **"No PDFs found"**
- Make sure you have PDF files in `./pdfs/` directory
- Check the file extensions are `.pdf`

### **"Docling not available"**
- Install: `pip install docling`
- First run will download models (takes time)

### **"Marker not available"**
- Install: `pip install marker-pdf`
- May need additional dependencies

### **"Tesseract not available"**
- Install Python wrapper: `pip install pytesseract`
- Install Tesseract engine: Download from GitHub releases
- Add to PATH or configure manually

### **"Permission errors"**
- Run from the correct directory
- Check file permissions on PDFs

---

## 🎯 **FOR YOUR MEETING**

**Show your mentor:**
1. **Run the benchmark**: `python run_real_ocr_benchmark.py`
2. **Show the outputs**: Navigate to the generated folder
3. **Open extracted texts**: Show actual OCR results side-by-side
4. **Display summary**: Show the CSV with quantitative comparisons
5. **Explain metrics**: Character accuracy, processing time, etc.

**Key points:**
- ✅ **Real OCR systems working**: Docling, Marker actually processing
- ✅ **Actual scientific PDFs**: Not simulated data
- ✅ **Quantitative comparison**: Measurable performance differences
- ✅ **Organized outputs**: Professional file structure
- ✅ **Ready for analysis**: CSV files for further processing

---

## 🚀 **QUICK START**

```bash
# 1. Make sure you're in the right directory
cd d:\extralit-benchmark\papers-ocr-benchmarks

# 2. Run the real benchmark
python run_real_ocr_benchmark.py

# 3. Check the outputs
ls ./output/

# 4. View a sample extracted text
cat ./output/real_ocr_benchmark_*/extracted_texts/*_Docling.txt | head -50
```

**That's it! Your benchmark will run and save everything to organized folders.** 🎉
