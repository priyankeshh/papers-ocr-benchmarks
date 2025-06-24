# OCR Benchmarking System for Scientific Literature

This project implements a comprehensive benchmarking framework to evaluate and compare OCR systems on scientific literature, developed as part of the Enhanced AI OCR Extraction Pipeline GSoC project for Extralit.

## Overview

The benchmarking system evaluates OCR systems across multiple dimensions critical for scientific document processing:

- **Text Extraction Accuracy**: Character, word, and line-level accuracy
- **Structure Preservation**: Headers, paragraphs, equations, tables, figures
- **Processing Performance**: Speed, efficiency, resource usage
- **Scientific Content Handling**: Formulas, notation, references
- **Cost Analysis**: For API-based services

## OCR Systems Evaluated

### Required
- **Marker** (Priority system as specified in GSoC proposal)

### Additional Systems (Choose 4 from)
- PyMuPDF + OpenCV
- Mistral OCR
- Nanonets OCR
- Gemini VLM
- SmolDocling
- OlmOCR
- Docling

## Project Structure

```
papers-ocr-benchmarks/
├── src/
│   ├── metrics/           # Evaluation metrics implementation
│   ├── ocr_systems/       # OCR system integrations
│   ├── benchmarking/      # Core benchmarking framework
│   ├── data/              # Dataset preparation and management
│   └── utils/             # Utility functions
├── pdfs/                  # Test dataset of scientific papers
├── results/               # Benchmark results and analysis
├── notebooks/             # Google Colab notebooks
└── docs/                  # Documentation
```

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run benchmark: `python src/benchmarking/run_benchmark.py`
3. View results in the generated Colab notebook

## Deliverables

- [x] OCR evaluation metrics design
- [ ] Standardized testing framework
- [ ] Marker OCR integration
- [ ] Additional OCR systems (2 minimum for initial deliverable)
- [ ] Initial benchmark results
- [ ] Google Colab notebook with findings

## GSoC Project Context

This benchmarking system supports the Enhanced AI OCR Extraction Pipeline project, focusing on improving table and text extraction from scientific papers using advanced ML techniques. See `Enhanced AI OCR Extraction Pipeline for Scientific Literature.md` for full project details.