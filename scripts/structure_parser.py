#!/usr/bin/env python3
"""
Structure Parser for OCR Outputs

This script analyzes the structured output from different OCR systems
to evaluate how well they preserve document structure and layout.
"""

import json
import re
from pathlib import Path
from datetime import datetime
import pandas as pd

class DocumentStructureParser:
    """Parse document structure from OCR outputs"""
    
    def __init__(self):
        self.results_dir = Path("./results")
        self.examples_dir = Path("./examples/outputs")
        self.examples_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_marker_structure(self, text):
        """Parse Marker OCR output (Markdown format)"""
        structure = {
            "ocr_system": "Marker",
            "format": "markdown",
            "timestamp": datetime.now().isoformat(),
            "document_elements": {
                "title": None,
                "authors": [],
                "abstract": None,
                "sections": [],
                "references": [],
                "equations": [],
                "tables": [],
                "figures": [],
                "captions": []
            },
            "reading_order": [],
            "metadata": {
                "total_sections": 0,
                "total_paragraphs": 0,
                "has_structured_content": False
            }
        }
        
        lines = text.split('\n')
        current_section = None
        in_abstract = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Title detection (usually first large heading)
            if line.startswith('# ') and not structure["document_elements"]["title"]:
                title = line[2:].strip()
                structure["document_elements"]["title"] = title
                structure["reading_order"].append({"type": "title", "content": title, "line": i})
            
            # Section headers
            elif line.startswith('## '):
                section_title = line[3:].strip()
                current_section = {
                    "title": section_title,
                    "content": [],
                    "subsections": []
                }
                structure["document_elements"]["sections"].append(current_section)
                structure["reading_order"].append({"type": "section_header", "content": section_title, "line": i})
                structure["metadata"]["total_sections"] += 1
                
                # Check for abstract
                if "abstract" in section_title.lower():
                    in_abstract = True
            
            # Subsection headers
            elif line.startswith('### '):
                subsection_title = line[4:].strip()
                if current_section:
                    current_section["subsections"].append({
                        "title": subsection_title,
                        "content": []
                    })
                structure["reading_order"].append({"type": "subsection_header", "content": subsection_title, "line": i})
            
            # Authors (often after title, before abstract)
            elif not structure["document_elements"]["authors"] and self._looks_like_authors(line):
                authors = self._extract_authors(line)
                structure["document_elements"]["authors"] = authors
                structure["reading_order"].append({"type": "authors", "content": authors, "line": i})
            
            # Equations (LaTeX or mathematical expressions)
            elif self._is_equation(line):
                equation = self._clean_equation(line)
                structure["document_elements"]["equations"].append(equation)
                structure["reading_order"].append({"type": "equation", "content": equation, "line": i})
            
            # Tables
            elif self._is_table_row(line):
                table_content = self._extract_table_context(lines, i)
                if table_content:
                    structure["document_elements"]["tables"].append(table_content)
                    structure["reading_order"].append({"type": "table", "content": table_content, "line": i})
            
            # Figures and captions
            elif self._is_figure_reference(line):
                figure_ref = self._extract_figure_info(line)
                structure["document_elements"]["figures"].append(figure_ref)
                structure["reading_order"].append({"type": "figure", "content": figure_ref, "line": i})
            
            # References
            elif self._is_reference(line):
                ref = self._clean_reference(line)
                structure["document_elements"]["references"].append(ref)
                structure["reading_order"].append({"type": "reference", "content": ref, "line": i})
            
            # Regular paragraphs
            elif len(line) > 50:  # Likely paragraph content
                if in_abstract and not structure["document_elements"]["abstract"]:
                    structure["document_elements"]["abstract"] = line
                    structure["reading_order"].append({"type": "abstract", "content": line, "line": i})
                    in_abstract = False
                else:
                    if current_section:
                        current_section["content"].append(line)
                    structure["reading_order"].append({"type": "paragraph", "content": line[:100] + "...", "line": i})
                    structure["metadata"]["total_paragraphs"] += 1
        
        # Set metadata
        structure["metadata"]["has_structured_content"] = len(structure["document_elements"]["sections"]) > 0
        
        return structure
    
    def parse_docling_structure(self, text):
        """Parse Docling OCR output"""
        structure = {
            "ocr_system": "Docling",
            "format": "markdown_enhanced",
            "timestamp": datetime.now().isoformat(),
            "document_elements": {
                "title": None,
                "authors": [],
                "abstract": None,
                "sections": [],
                "references": [],
                "equations": [],
                "tables": [],
                "figures": [],
                "captions": []
            },
            "reading_order": [],
            "metadata": {
                "total_sections": 0,
                "total_paragraphs": 0,
                "has_structured_content": False
            }
        }
        
        # Docling often has better structure preservation
        # Similar parsing logic but adapted for Docling's output format
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Docling-specific patterns
            if line.startswith('<!-- image -->'):
                structure["reading_order"].append({"type": "image_marker", "content": "Image detected", "line": i})
            elif line.startswith('##'):
                section_title = line.lstrip('#').strip()
                structure["document_elements"]["sections"].append({
                    "title": section_title,
                    "content": []
                })
                structure["reading_order"].append({"type": "section_header", "content": section_title, "line": i})
                structure["metadata"]["total_sections"] += 1
            elif len(line) > 50:
                structure["reading_order"].append({"type": "paragraph", "content": line[:100] + "...", "line": i})
                structure["metadata"]["total_paragraphs"] += 1
        
        structure["metadata"]["has_structured_content"] = len(structure["document_elements"]["sections"]) > 0
        return structure
    
    def parse_pymupdf_structure(self, text):
        """Parse PyMuPDF output (plain text)"""
        structure = {
            "ocr_system": "PyMuPDF",
            "format": "plain_text",
            "timestamp": datetime.now().isoformat(),
            "document_elements": {
                "title": None,
                "authors": [],
                "abstract": None,
                "sections": [],
                "references": [],
                "equations": [],
                "tables": [],
                "figures": [],
                "captions": []
            },
            "reading_order": [],
            "metadata": {
                "total_sections": 0,
                "total_paragraphs": 0,
                "has_structured_content": False
            }
        }
        
        # PyMuPDF provides less structure, so we need to infer it
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Page markers
            if line.startswith('=== Page'):
                structure["reading_order"].append({"type": "page_break", "content": line, "line": i})
            elif len(line) > 50:
                structure["reading_order"].append({"type": "paragraph", "content": line[:100] + "...", "line": i})
                structure["metadata"]["total_paragraphs"] += 1
        
        return structure
    
    def _looks_like_authors(self, line):
        """Check if line looks like author names"""
        # Simple heuristic: contains names with potential affiliations
        return bool(re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', line)) and len(line.split()) < 20
    
    def _extract_authors(self, line):
        """Extract author names from line"""
        # Simple extraction - can be enhanced
        return [name.strip() for name in line.split(',') if name.strip()]
    
    def _is_equation(self, line):
        """Check if line contains mathematical equation"""
        return bool(re.search(r'\$.*\$|\\[a-zA-Z]+|=.*[+\-*/]', line))
    
    def _clean_equation(self, line):
        """Clean and extract equation"""
        return line.strip()
    
    def _is_table_row(self, line):
        """Check if line is part of a table"""
        return '|' in line and line.count('|') >= 2
    
    def _extract_table_context(self, lines, start_idx):
        """Extract table content around the detected row"""
        # Simple table extraction
        table_lines = []
        for i in range(max(0, start_idx-2), min(len(lines), start_idx+3)):
            if '|' in lines[i]:
                table_lines.append(lines[i].strip())
        return '\n'.join(table_lines) if table_lines else None
    
    def _is_figure_reference(self, line):
        """Check if line references a figure"""
        return bool(re.search(r'[Ff]igure\s+\d+|[Ff]ig\.?\s+\d+', line))
    
    def _extract_figure_info(self, line):
        """Extract figure information"""
        return line.strip()
    
    def _is_reference(self, line):
        """Check if line is a reference"""
        return bool(re.search(r'^\[\d+\]|\(\d{4}\)|et\s+al\.', line))
    
    def _clean_reference(self, line):
        """Clean reference text"""
        return line.strip()
    
    def analyze_all_outputs(self):
        """Analyze all OCR outputs and create structured JSON files"""
        
        print("🔍 ANALYZING OCR STRUCTURE OUTPUTS")
        print("=" * 50)
        
        # Find all OCR output files (look in subdirectories too)
        ocr_files = list(self.results_dir.glob("**/*_*.txt"))
        
        if not ocr_files:
            print("❌ No OCR output files found in results directory")
            return
        
        # Group files by PDF
        pdf_groups = {}
        for file in ocr_files:
            parts = file.stem.split('_')
            if len(parts) >= 2:
                pdf_name = '_'.join(parts[:-1])
                ocr_system = parts[-1]
                
                if pdf_name not in pdf_groups:
                    pdf_groups[pdf_name] = {}
                pdf_groups[pdf_name][ocr_system] = file
        
        # Process each PDF
        all_analyses = {}
        
        for pdf_name, systems in pdf_groups.items():
            print(f"\n📄 Analyzing: {pdf_name}")
            
            pdf_analysis = {
                "pdf_name": pdf_name,
                "timestamp": datetime.now().isoformat(),
                "ocr_systems": {}
            }
            
            for system_name, file_path in systems.items():
                print(f"  🔄 Processing {system_name}...")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse based on OCR system
                if system_name == "Marker":
                    structure = self.parse_marker_structure(content)
                elif system_name == "Docling":
                    structure = self.parse_docling_structure(content)
                elif system_name == "PyMuPDF":
                    structure = self.parse_pymupdf_structure(content)
                else:
                    continue
                
                pdf_analysis["ocr_systems"][system_name] = structure
                
                # Save individual system analysis
                output_file = self.examples_dir / f"{pdf_name}_{system_name}_structure.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(structure, f, indent=2, ensure_ascii=False)
                
                print(f"    ✅ Saved: {output_file}")
            
            all_analyses[pdf_name] = pdf_analysis
        
        # Save combined analysis
        combined_file = self.examples_dir / "combined_structure_analysis.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(all_analyses, f, indent=2, ensure_ascii=False)
        
        # Create comparison summary
        self.create_structure_comparison(all_analyses)
        
        print(f"\n✅ Structure analysis complete!")
        print(f"📁 JSON outputs saved to: {self.examples_dir}")
        print(f"📊 Combined analysis: {combined_file}")
    
    def create_structure_comparison(self, analyses):
        """Create a comparison summary of structure parsing"""
        
        comparison_data = []
        
        for pdf_name, pdf_data in analyses.items():
            for system_name, structure in pdf_data["ocr_systems"].items():
                metadata = structure["metadata"]
                elements = structure["document_elements"]
                
                comparison_data.append({
                    "PDF": pdf_name,
                    "OCR_System": system_name,
                    "Total_Sections": metadata["total_sections"],
                    "Total_Paragraphs": metadata["total_paragraphs"],
                    "Has_Structured_Content": metadata["has_structured_content"],
                    "Title_Detected": elements["title"] is not None,
                    "Authors_Detected": len(elements["authors"]) > 0,
                    "Abstract_Detected": elements["abstract"] is not None,
                    "Equations_Found": len(elements["equations"]),
                    "Tables_Found": len(elements["tables"]),
                    "Figures_Found": len(elements["figures"]),
                    "References_Found": len(elements["references"]),
                    "Reading_Order_Items": len(structure["reading_order"])
                })
        
        # Save comparison CSV
        df = pd.DataFrame(comparison_data)
        comparison_file = self.examples_dir / "structure_comparison.csv"
        df.to_csv(comparison_file, index=False)
        
        print(f"📊 Structure comparison saved: {comparison_file}")
        
        # Print summary
        print(f"\n📈 STRUCTURE PARSING SUMMARY")
        print("=" * 50)
        print(df.to_string(index=False))

if __name__ == "__main__":
    parser = DocumentStructureParser()
    parser.analyze_all_outputs()
