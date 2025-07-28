#!/usr/bin/env python3
"""
Client example for the Enhanced AI OCR Extraction Pipeline Server
"""

import requests
import json
from pathlib import Path
import argparse


def upload_pdf_for_processing(
    pdf_path: str,
    server_url: str = "http://localhost:8001",
    chunk_mode: str = "header",
    chunk_size: int = 1024,
    chunk_overlap: int = 128,
    use_ocr: str = "auto"
):
    """
    Upload a PDF to the server for processing
    
    Args:
        pdf_path: Path to the PDF file
        server_url: Server URL (default: http://localhost:8001)
        chunk_mode: 'header' or 'llama_token'
        chunk_size: Size of chunks (for llama_token mode)
        chunk_overlap: Overlap between chunks
        use_ocr: 'auto', 'true', or 'false'
    """
    
    # Prepare the files and data
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {
            'chunk_mode': chunk_mode,
            'chunk_size': str(chunk_size),
            'chunk_overlap': str(chunk_overlap),
            'use_ocr': use_ocr
        }
        
        try:
            print(f"📤 Uploading {pdf_path} to {server_url}/predict")
            print(f"⚙️  Processing options: chunk_mode={chunk_mode}, chunk_size={chunk_size}, use_ocr={use_ocr}")
            
            response = requests.post(
                f"{server_url}/predict",
                files=files,
                data=data,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Processing successful!")
                print(f"📊 Extracted {result.get('chunks_count', 0)} chunks")
                
                # Print first chunk as example
                if result.get('chunks') and len(result['chunks']) > 0:
                    first_chunk = result['chunks'][0]
                    print(f"\n--- Example Chunk ---")
                    print(f"Header: {first_chunk.get('metadata', {}).get('header', 'N/A')}")
                    print(f"Text preview: {first_chunk.get('text', '')[:200]}...")
                
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out. The PDF might be too large or complex.")
            return None
        except requests.exceptions.ConnectionError:
            print(f"🔌 Could not connect to server at {server_url}")
            print("Make sure the server is running with: python server.py")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None


def check_server_health(server_url: str = "http://localhost:8001"):
    """Check if the server is running and healthy"""
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server is healthy at {server_url}")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 Could not connect to server at {server_url}")
        return False
    except Exception as e:
        print(f"❌ Error checking server health: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for Enhanced AI OCR Extraction Pipeline")
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    parser.add_argument("--server", default="http://localhost:8001", help="Server URL")
    parser.add_argument("--chunk-mode", default="header", choices=["header", "llama_token"], 
                       help="Chunking mode")
    parser.add_argument("--chunk-size", type=int, default=1024, help="Chunk size (for llama_token mode)")
    parser.add_argument("--chunk-overlap", type=int, default=128, help="Chunk overlap")
    parser.add_argument("--use-ocr", default="auto", choices=["auto", "true", "false"], 
                       help="OCR usage policy")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Check if PDF file exists
    if not Path(args.pdf_path).exists():
        print(f"❌ PDF file not found: {args.pdf_path}")
        exit(1)
    
    # Check server health first
    print("🔍 Checking server health...")
    if not check_server_health(args.server):
        print("💡 Start the server with: python server.py")
        exit(1)
    
    # Process the PDF
    result = upload_pdf_for_processing(
        pdf_path=args.pdf_path,
        server_url=args.server,
        chunk_mode=args.chunk_mode,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        use_ocr=args.use_ocr
    )
    
    # Save results if requested
    if result and args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Results saved to {args.output}")
