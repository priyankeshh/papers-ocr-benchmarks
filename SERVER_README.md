# Enhanced AI OCR Extraction Pipeline Server

This directory contains a LitServe-based server for the Enhanced AI OCR Extraction Pipeline, designed for demo purposes and production deployment.

## Features

- **PDF Upload & Processing**: Upload PDFs via HTTP API
- **Intelligent OCR**: Automatically detects scanned vs born-digital PDFs
- **Multiple Chunking Strategies**: 
  - Header-based chunking (semantic sections)
  - Token-based chunking (LlamaMarkdownReader)
- **Structured Output**: Returns hierarchical markdown with metadata
- **GPU Support**: Automatic GPU acceleration when available
- **Production Ready**: Built on LitServe for high-throughput serving

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python server.py
```

The server will start on `http://localhost:8000` by default.

### 3. Test with Example Client

```bash
# Process a PDF with default settings
python client_example.py "pdfs/Allossogbe_et_al_2017_Mal_J.pdf"

# Use header-based chunking and save results
python client_example.py "pdfs/your_paper.pdf" --chunk-mode header --output results.json

# Force OCR processing
python client_example.py "pdfs/scanned_paper.pdf" --use-ocr true
```

## Server Configuration

### Command Line Options

```bash
python server.py --help
```

Available options:
- `--port`: Server port (default: 8000)
- `--host`: Host to bind to (default: 0.0.0.0)
- `--accelerator`: Device type (auto, cpu, gpu)
- `--workers`: Workers per device (default: 1)
- `--timeout`: Request timeout in seconds (default: 300)

### Example Production Setup

```bash
# Run on GPU with multiple workers
python server.py --port 8000 --accelerator gpu --workers 2 --timeout 600

# CPU-only setup
python server.py --port 8001 --accelerator cpu --workers 4
```

## API Usage

### Endpoint: `POST /predict`

Upload a PDF file with processing options:

**Request Format:** `multipart/form-data`

- `file`: PDF file (required)
- `chunk_mode`: "header" or "llama_token" (optional, default: "header")
- `chunk_size`: Integer (optional, default: 1024)
- `chunk_overlap`: Integer (optional, default: 128)
- `use_ocr`: "auto", "true", or "false" (optional, default: "auto")

**Response Format:** JSON

```json
{
  "status": "success",
  "chunks_count": 15,
  "chunks": [
    {
      "text": "# Introduction\n\nThis paper presents...",
      "metadata": {
        "header": "Introduction",
        "source_pdf": "/path/to/file.pdf",
        "chunk_index": 0,
        "start_line": 0,
        "end_line": 25
      }
    }
  ],
  "processing_info": {
    "chunk_mode": "header",
    "chunk_size": 1024,
    "chunk_overlap": 128,
    "use_ocr": "auto"
  }
}
```

### Example cURL Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@your_paper.pdf" \
  -F "chunk_mode=header" \
  -F "use_ocr=auto"
```

### Python Client Example

```python
import requests

with open("paper.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/predict",
        files={"file": f},
        data={
            "chunk_mode": "header",
            "use_ocr": "auto"
        }
    )
    
result = response.json()
print(f"Extracted {result['chunks_count']} chunks")
```

## Pipeline Details

### 1. PDF Preprocessing
- Automatic detection of scanned vs born-digital PDFs
- OCRmyPDF integration for image cleanup (rotation, deskewing)
- Configurable OCR behavior (auto, force, disable)

### 2. Text Extraction
- PyMuPDF4LLM for hierarchical markdown extraction
- Table removal and content cleaning
- Preservation of document structure and headings

### 3. Chunking Strategies

**Header-based Chunking (Recommended)**
- Chunks content by markdown headers (`#`, `##`, etc.)
- Preserves semantic document structure
- Ideal for academic papers and structured documents

**Token-based Chunking**
- Fixed-size chunks with configurable overlap
- Better for uniform processing requirements
- Uses LlamaMarkdownReader internally

## Integration with Vector Databases

The chunked output is designed to work seamlessly with vector databases like Weaviate:

```python
import weaviate

client = weaviate.Client("http://localhost:8080")

for chunk in result['chunks']:
    client.data_object.create({
        "content": chunk['text'],
        "header": chunk['metadata'].get('header', ''),
        "source": chunk['metadata'].get('source_pdf', ''),
        "chunk_index": chunk['metadata'].get('chunk_index', 0)
    }, class_name="DocumentChunk")
```

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if port is already in use
   - Verify all dependencies are installed
   - Check OCRmyPDF system dependencies

2. **OCR fails**
   - Ensure Tesseract is installed
   - On Windows: Install via `choco install tesseract`
   - Check PDF file is not corrupted

3. **Memory issues**
   - Reduce workers per device
   - Use CPU instead of GPU for large files
   - Increase system RAM or use smaller PDFs

### Logs

The server logs all operations to `extract_pipeline.log`. Check this file for detailed error information.

## Development

### Extending the Pipeline

To add new processing features:

1. Modify the `EnhancedOCRAPI` class in `server.py`
2. Add new parameters to `decode_request()`
3. Implement logic in `predict()` or helper methods
4. Update the client example accordingly

### Testing

```bash
# Test server health
curl http://localhost:8000/health

# Test with sample PDF
python client_example.py "pdfs/sample.pdf" --output test_results.json
```

## Production Deployment

For production deployment, consider:

1. **Load Balancing**: Use nginx or similar for multiple server instances
2. **GPU Management**: Monitor GPU memory usage and implement cleanup
3. **File Storage**: Implement proper temporary file cleanup
4. **Security**: Add authentication and file validation
5. **Monitoring**: Integrate with monitoring systems (Prometheus, etc.)

## Related Projects

- [Extralit.ai](https://extralit.ai/) - Main project website
- [PyMuPDF4LLM](https://pymupdf4llm.readthedocs.io/) - PDF extraction library
- [LitServe](https://lightning.ai/litserve) - AI model serving engine
- [OCRmyPDF](https://ocrmypdf.readthedocs.io/) - PDF OCR processing
