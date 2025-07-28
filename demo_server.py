#!/usr/bin/env python3
"""
Demo script for the Enhanced AI OCR Extraction Pipeline Server
This script demonstrates the complete workflow from server startup to PDF processing.
"""

import subprocess
import time
import requests
import json
from pathlib import Path
import threading
import sys


class ServerDemo:
    def __init__(self, server_port=8000):
        self.server_port = server_port
        self.server_url = f"http://localhost:{server_port}"
        self.server_process = None
        
    def start_server(self):
        """Start the server in the background"""
        print("🚀 Starting Enhanced AI OCR Server...")
        
        try:
            self.server_process = subprocess.Popen([
                sys.executable, "server.py", 
                "--port", str(self.server_port),
                "--accelerator", "auto",
                "--workers", "1"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for server to start up
            print("⏳ Waiting for server to initialize...")
            max_retries = 30
            for i in range(max_retries):
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Server is running at {self.server_url}")
                        return True
                except requests.exceptions.ConnectionError:
                    time.sleep(2)
                    print(f"⏳ Retry {i+1}/{max_retries}...")
                    
            print("❌ Server failed to start within timeout period")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the server"""
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait(timeout=10)
            print("✅ Server stopped")
    
    def demo_pdf_processing(self, pdf_path):
        """Demonstrate PDF processing with different configurations"""
        if not Path(pdf_path).exists():
            print(f"❌ PDF file not found: {pdf_path}")
            return
            
        print(f"\n📄 Demonstrating PDF processing with: {pdf_path}")
        
        # Demo 1: Header-based chunking
        print("\n--- Demo 1: Header-based Chunking ---")
        result1 = self.process_pdf(pdf_path, chunk_mode="header", use_ocr="auto")
        
        if result1:
            print(f"✅ Header-based chunking: {result1['chunks_count']} chunks")
            if result1['chunks']:
                chunk = result1['chunks'][0]
                print(f"📋 First chunk header: {chunk['metadata'].get('header', 'N/A')}")
                print(f"📝 Text preview: {chunk['text'][:150]}...")
        
        # Demo 2: Token-based chunking
        print("\n--- Demo 2: Token-based Chunking ---")
        result2 = self.process_pdf(pdf_path, chunk_mode="llama_token", chunk_size=512)
        
        if result2:
            print(f"✅ Token-based chunking: {result2['chunks_count']} chunks")
            if result2['chunks']:
                chunk = result2['chunks'][0]
                print(f"📝 First chunk preview: {chunk['text'][:150]}...")
        
        # Demo 3: Forced OCR
        print("\n--- Demo 3: Forced OCR Processing ---")
        result3 = self.process_pdf(pdf_path, chunk_mode="header", use_ocr="true")
        
        if result3:
            print(f"✅ Forced OCR processing: {result3['chunks_count']} chunks")
        
        return [result1, result2, result3]
    
    def process_pdf(self, pdf_path, chunk_mode="header", chunk_size=1024, use_ocr="auto"):
        """Process a single PDF with given parameters"""
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'chunk_mode': chunk_mode,
                    'chunk_size': str(chunk_size),
                    'use_ocr': use_ocr
                }
                
                response = requests.post(
                    f"{self.server_url}/predict",
                    files=files,
                    data=data,
                    timeout=120
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"❌ Request failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return None
    
    def run_demo(self, pdf_paths=None):
        """Run the complete demo"""
        print("🎯 Enhanced AI OCR Extraction Pipeline Demo")
        print("=" * 50)
        
        # Use default PDF if none provided
        if not pdf_paths:
            pdf_paths = [
                "pdfs/Allossogbe_et_al_2017_Mal_J.pdf",
                "pdfs/Mbogo_et_al_1996_Med_Vet_Ento.pdf"
            ]
        
        # Filter to existing PDFs
        existing_pdfs = [p for p in pdf_paths if Path(p).exists()]
        if not existing_pdfs:
            print("❌ No sample PDFs found. Please ensure PDFs are available in the pdfs/ directory.")
            return
        
        try:
            # Start server
            if not self.start_server():
                return
            
            # Process each PDF
            all_results = {}
            for pdf_path in existing_pdfs:
                results = self.demo_pdf_processing(pdf_path)
                all_results[pdf_path] = results
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 Demo Summary")
            print("=" * 50)
            
            for pdf_path, results in all_results.items():
                print(f"\n📄 {Path(pdf_path).name}:")
                for i, result in enumerate(results, 1):
                    if result:
                        mode = ["Header-based", "Token-based", "Forced OCR"][i-1]
                        print(f"  {mode}: {result['chunks_count']} chunks")
                    else:
                        print(f"  Demo {i}: Failed")
            
            # Save detailed results
            output_file = "demo_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Detailed results saved to: {output_file}")
            
        finally:
            # Always stop server
            self.stop_server()
        
        print("\n🎉 Demo completed!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Demo for Enhanced AI OCR Extraction Pipeline")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--pdfs", nargs='+', help="PDF files to process")
    
    args = parser.parse_args()
    
    # Create and run demo
    demo = ServerDemo(server_port=args.port)
    demo.run_demo(pdf_paths=args.pdfs)
