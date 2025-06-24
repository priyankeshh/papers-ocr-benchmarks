**Enhanced AI OCR Extraction Pipeline for Scientific Literature**

Candidate Info

\- **Name:** Priyankesh

\- **GitHub:** [https://github.com/priyankeshh](https://github.com/priyankeshh)

\- **Email:** priyankeshom@gmail.com

\- **Twitter/X:** [https://x.com/priyankeshhh](https://x.com/priyankeshhh)

\- **LinkedIn:** [https://www.linkedin.com/in/priyankesh/](https://www.linkedin.com/in/priyankesh/)

\- **University Course:** Bachelor of Technology in Artificial Intelligence and Machine Learning

\- **University:** Guru Gobind Singh Indraprastha University (GGSIPU) East Delhi Campus

\- **Time Zone:** Indian Standard Time (GMT+5:30)

**Bio:**

I am currently in my third year of studying B.Tech in Artificial Intelligence and Machine Learning at Guru Gobind Singh Indraprastha University. My focus in AI and machine learning has been mainly on vision and language models. I've worked on hands-on projects like OCR tasks, recognizing handwritten digits, and natural language processing. I have gained considerable experience with computer vision models and have leveraged the Gemini API on significant projects. 

My skill set includes Python, OpenCV, PyMuPDF, and Hugging Face models, through which I have fine-tuned various applications. Over the past two years, I have actively contributed to open-source initiatives, collaborating with organizations like AOSSIE, SDC, and SUGAR LABS in addition to several smaller contributions. Engaging with open-source projects has been a vital part of my learning path, and I truly enjoy creating solutions that benefit the broader community.

Project Overview

\- **Project:** Enhanced AI OCR Extraction Pipeline

\- **Project Idea/Plan:** Project Idea \#2 \- Improving table and text extraction from scientific papers using advanced ML techniques

\- **Expected Time (hours):** 175 hours

Abstract

Scientific literature contains valuable data often locked in complex tables, figures, and structured text that traditional OCR systems struggle to extract accurately. This project aims to revolutionize Extralit's extraction capabilities by developing an enhanced OCR pipeline that combines the strengths of modern Vision-Language Models (VLMs), specialized table detection algorithms, and efficient document structure recognition. By integrating Marker's advanced text extraction with Table-Transformer's table detection capabilities and optimizing the pipeline for batch processing, we will create a robust system capable of processing hundreds of scientific papers with significantly improved accuracy and reduced computational costs. The solution will focus mainly on complex table formats standard in life science research, where current approaches often require substantial human correction.

Mentors

\- Jonny Tran (nhat.c.tran@gmail.com)

\- Dianne Ting (dianneting.design@gmail.com)

Technical Details

Task 1: Exploration and Benchmarking of OCR Technologies

I will evaluate various approaches for scientific document extraction, focusing on their performance with complex tables and structured text:

1\. **Vision-Language Models (VLMs)**:

\- Test GPT-4V, Claude 3, and Gemini for table structure recognition

\- Evaluate prompt engineering techniques for optimal extraction	

\- Benchmark performance against human-annotated gold standards

2\. **Specialized Table Extraction Models**:

\- Implement and evaluate Table-Transformer models based on the PubTables-1M research

\- Reference: [PubTables-1M paper](https://openaccess.thecvf.com/content/CVPR2022/html/Smock_PubTables-1M_Towards_Comprehensive_Table_Extraction_From_Unstructured_Documents_CVPR_2022_paper.html)

\- Test integration with Extralit's existing pipeline in `argilla/src/extralit/extraction/` modules

3\. **Traditional ML Approaches**:

\- Evaluate PyMuPDF \+ OpenCV for layout analysis

\- Test Marker for improved text extraction

\- Reference: [https://github.com/VikParuchuri/marker](https://github.com/VikParuchuri/marker)

Based on preliminary research, I plan to implement a hybrid approach that:

\- Uses PyMuPDF for initial document parsing and structure detection

\- Applies specialized table detection models for complex tables

\- Leverages VLMs for ambiguous cases and post-processing

\- Implements custom post-processing to maintain document structure

I will work with Extralit's predefined document segment classes defined in `extralit/preprocessing/segment.py`, including:

\- `TextSegment`: For handling textual content with its page number, section hierarchy, and bounding box coordinates

\- `TableSegment`: For representing tables with their headers, structure, and position information

\- `FigureSegment`: For managing figures with their captions and spatial attributes

These pydantic classes will be extended as needed to support richer metadata and improved structure preservation throughout the extraction pipeline. The enhanced pipeline will maintain tracking of page numbers, section hierarchies, bounding box coordinates, and table/figure headers consistently across all document segments.

Code segments for modification:

\- `extralit/extraction/models/paper.py` \- Enhance the `PaperExtraction` class

\- `extralit/server/app.py` \- Add new API endpoints for the enhanced OCR pipeline

\- `extralit/preprocessing/segment.py` \- Extend segment classes with additional metadata needed for complex tables

Task 2: Document OCR Pipeline Implementation

I will develop a modular OCR pipeline with these components:

1\. **PDF Preprocessing**:

\- Implement page segmentation and normalization

\- Create image enhancement for better OCR quality

This image enhancement pipeline will be designed to handle both scanned and born-digital PDFs, with adaptive processing that detects and applies appropriate techniques for each type:

For scanned PDFs:

\- Apply advanced denoising algorithms to remove scanning artifacts and speckles

\- Implement adaptive binarization with optimized thresholding for text/background separation

\- Correct skew and rotation issues common in scanned documents

\- Use super-resolution techniques for low-resolution scans to improve character recognition

For born-digital PDFs:

\- Extract vector text when available for perfect accuracy

\- Apply specialized processing for embedded raster images within the PDF

\- Handle anti-aliasing artifacts at text boundaries that may confuse OCR

\- Preserve font information and embedded metadata when present

The pipeline will automatically detect document type (scanned vs. born-digital) and selectively apply the appropriate enhancement techniques. For hybrid PDFs (containing both scanned images and digital elements), the system will process different regions with the appropriate technique based on content type detection.

Since scientific literature often contains a mix of both types (particularly with older papers being scanned and newer ones being born-digital), this adaptive approach will ensure optimal extraction quality across the entire corpus.

\- Develop document structure analysis to identify sections, headings, and tables

2\. **Table Detection and Extraction**:

\- Implement table boundary detection using computer vision techniques

\- Create table structure recognition to identify rows, columns, and cells

\- Build cell content extraction with text alignment preservation

3\. **Text Extraction with Structure Preservation**:

\- Implement heading and section detection

\- Create paragraph and list recognition

\- Build document hierarchy preservation

The implementation will use a combination of:

\- PyMuPDF for PDF parsing

\- Computer vision libraries for layout analysis

\- Custom ML models for table structure recognition

\- Integration with Extralit's current document storage infrastructure, with awareness of planned migration from Weaviate to Elasticsearch for vector search

Task 3: Post-processing Pipeline

I will create a robust post-processing pipeline to:

1\. **Clean and Format Extracted Content**:

\- Implement text normalization and cleaning

\- Create table structure validation and correction

\- Build document structure reconstruction

2\. **Integrate with Existing Data Pipeline**:

\- Connect to Extralit's storage stack (Minio/S3)

\- Implement integration with vector database (Weaviate)

3\. **Optimize for Performance**:

\- Implement parallel processing for multiple documents

\- Create caching mechanisms for improved speed

\- Build resource usage optimization

Task 4: API Development and Integration

I will develop a comprehensive API that:

1\. **Provides Extraction Endpoints**:

\- Create FastAPI endpoints for document processing with minimal deployment requirements

\- Design a provider-agnostic architecture that can integrate multiple OCR services (Marker, Mistral OCR, etc.)

\- Implement progress monitoring and status reporting

\- Build error handling and recovery mechanisms

\- Optimize for low-cost deployment options, including Hugging Face Spaces

2\. **Integrates with Extralit Web UI**:

\- Create interfaces for viewing and correcting OCR outputs

\- Implement webhook system to notify downstream processes when OCR data is edited

\- Build integration points that trigger data updates across the system after corrections	

3\. **Ensures Security and Scalability**:

\- Implement authentication and authorization

\- Create rate limiting and resource management

\- Build logging and monitoring

Task 5: Evaluation and Documentation

I will create comprehensive evaluation metrics and documentation:

1\. **Performance Benchmarks**:

\- Implement accuracy metrics for text and table extraction

\- Create speed and resource usage benchmarks

\- Build cost analysis for large-scale processing

2\. **Documentation and Tutorials**:

\- Create technical documentation for the API

\- Write deployment guides for cloud platforms

\- Build tutorials for using the extraction pipeline

**Benefits to the Community**

This enhanced OCR extraction pipeline will benefit the scientific community in several ways:

1\. **Improved Data Extraction Accuracy**: Researchers will be able to extract data from complex scientific tables with higher accuracy, reducing manual correction time.

2\. **Faster Literature Processing**: The optimized pipeline will enable processing hundreds of papers efficiently, accelerating literature reviews and meta-analyses.

3\. **Cost-Effective Solution**: By combining traditional ML approaches with selective use of VLMs, the solution will be more cost-effective than pure LLM-based approaches.

4\. **Preservation of Document Structure**: The pipeline will maintain the hierarchical structure of documents, making extracted data more contextually relevant.

5\. **Integration with Existing Workflows**: Seamless integration with Extralit's web UI will allow researchers to monitor, correct, and validate extracted data within their existing workflows.

6\. **Open-Source Contribution**: The implementation will be fully open-source, allowing the community to build upon and improve the extraction capabilities.

**Deliverables and Timeline**

Timeline

### **Phase 1: Community Bonding (May 8 \- June 1\)**

**May 8 \- May 14: Community Bonding Initiation**

* Set up development environment with all required dependencies  
* Study Extralit's codebase structure and existing OCR pipeline  
* Meet with mentors to align on project goals and expectations  
* Create initial project roadmap and success metrics

**May 15 \- May 21: Technical Planning (Light workload due to practical exams)**

* Analyze existing table extraction algorithms in the codebase  
* Explore PyMuPDF and OpenCV integration possibilities  
* Begin collecting sample scientific papers for test dataset  
* Create project documentation template

**May 22 \- June 1: Research Preparation (Limited hours due to practical exams)**

* Study the API structure and integration points  
* Create a detailed technical specifications document  
* Set up basic evaluation framework structure

### **Phase 2: Early Coding with Exam Considerations (June 2 \- July 18\)**

**June 2 \- June 19: Initial Implementation (Reduced workload during theory exams)**

* Begin testing GPT-4V and Gemini on simple table examples  
* Research existing approaches in literature  
* Set up evaluation metrics  
* Implement basic preprocessing components  
* Weekly short sync with mentors to maintain engagement  
* *Note: Limited availability (5-10 hours/week) during exam period*

**June 20 \- July 3: Accelerated Core Implementation (Post-exams)**

* Complete full benchmarking of VLMs and specialized models  
* Finalize technology selection based on evaluation results  
* Implement page segmentation with PyMuPDF  
* Create image preprocessing pipeline  
* Build document structure analysis to identify content regions

**July 4 \- July 13: Table Detection Implementation (Midterm Milestone)**

* Implement table boundary detection using fine-tuned Table-Transformer  
* Create initial table structure recognition algorithm  
* Build cell boundary detection system  
* Develop unit tests for table detection  
* Prepare midterm evaluation deliverables

**July 14 \- July 18: Midterm Evaluation Period**

* Complete all documentation for the midterm evaluation  
* Prepare a demo of the current functionality  
* Review progress with mentors  
* Plan adjustments for the second half if needed  
* Submit midterm evaluation

### 

### **Phase 3: Advanced Features (July 19 \- August 25\)**

**July 19 \- July 26: Table Structure Recognition**

* Implement table structure recognition for rows and columns  
* Create specialized handling for merged cells  
* Build a cell content extraction with formatting preservation  
* Complete unit tests for the table extraction module

**July 27 \- August 2: Text Extraction Implementation**

* Implement heading and section detection  
* Create a paragraph and list recognition  
* Build document hierarchy preservation  
* Implement output formatting and cleaning

**August 3 \- August 9: API Development and Integration**

* Create FastAPI endpoints for document processing with minimal deployment requirements  
* Design a provider-agnostic architecture that can integrate multiple OCR services (Marker, Mistral OCR)  
* Implement progress monitoring and status reporting  
* Build error handling and recovery mechanisms  
* Optimize for low-cost deployment options, including Hugging Face Spaces

**August 10 \- August 17: Optimization and Testing**

* Implement UI hooks for monitoring extraction progress  
* Create interfaces for viewing and correcting OCR outputs for tables and document elements  
* Implement a webhook system to trigger LLM data extraction processes when OCR data is edited  
* Build visualization components for extracted tables  
* Design a testing framework for webhook reliability

**August 18 \- August 25: Final Refinement and Documentation**

* Address feedback from mentors  
* Fix bugs and edge cases  
* Finalize technical documentation  
* Create user guides and tutorials  
* Prepare final presentation materials

### **Phase 4: Final Submission (August 26 \- September 1\)**

**August 26 \- September 1: Final Submission Period**

* Address feedback from mentors  
* Fix bugs and edge cases  
* Finalize technical documentation  
* Create user guides and tutorials  
* Prepare final presentation materials

**Previous Contributions to the Project**

Though new to Extralit, I have already made a few contributions to improve the development experience and code reliability:

* [**\#31**](https://github.com/extralit/extralit/pull/31) **\[DOCS\] Included a comprehensive setup instruction for Extralit development**  
  * After spending two days figuring out the environment setup on my own, I created detailed documentation to help other contributors get started more easily  
      
* [**\#42**](https://github.com/extralit/extralit/pull/42) **feat: add Redis service to Docker Compose**  
  * I noticed that Redis (which is essential for the application to function properly) was missing from the Docker Compose configuration. I added the missing docker dependencies  
      
* [**\#36**](https://github.com/extralit/extralit/pull/36) **Enhanced Error Handling for PDF Processing Pipeline**  
  * This PR adds robust error handling to the document processing pipeline to prevent failures when processing problematic PDFs. The implementation includes a decorator-based approach that provides consistent error handling across all document processing functions, along with granular exception handling within the create\_or\_load\_llmsherpa\_segments function as a template for other processors.

**Why This Project?**

I'm really excited about this project because it blends machine learning, computer vision, and scientific research. Having worked with scientific papers, I know how tough it can be for researchers to pull out structured data. The current way of doing this manually takes a lot of time and can lead to mistakes. I truly think that improving the OCR process can help speed up scientific work.

The technical challenges of this project are particularly exciting to me. Merging traditional computer vision methods with new VLMs could lead to a great solution that takes advantage of both. I'm also interested in the end-to-end nature of the project, from preprocessing PDFs to delivering a user-friendly API that integrates with the existing Extralit ecosystem.

Furthermore, I believe that open-source tools like Extralit are crucial for democratizing access to advanced data extraction capabilities. By contributing to this project, I can help make scientific literature more accessible and analyzable for researchers worldwide.

**Availability**

I can commit to working 25-30 hours per week on this project throughout the GSoC period, with a reduced commitment of 5-10 hours per week during my university theory exams (June 2-19). After June 19, I will have no other major commitments and can dedicate full attention to the project.

If I fall behind schedule, I will:

1\. Immediately communicate with my mentors about the delay

2\. Allocate additional hours during the following week to catch up

3\. Prioritize critical path items to ensure core functionality is delivered on time

4\. If necessary, propose scope adjustments to ensure high-quality delivery of essential features

I will maintain regular communication with mentors through weekly meetings and daily updates on Slack.

**Post-GSoC**

After GSoC, I plan to continue contributing to Extralit in several ways:

1\. **Maintenance and Improvements**: I will continue to maintain the OCR pipeline, addressing bugs and implementing improvements based on user feedback.

2\. **Feature Expansion**: I'm interested in expanding the pipeline to handle additional document types and more complex scientific figures.

3\. **Community Support**: I plan to help new users and contributors understand and use the OCR pipeline through documentation, tutorials, and forum support.

4\. **Research Integration**: I would like to explore integrations with other scientific research tools and workflows to create a more comprehensive ecosystem for literature analysis.

Long-term, this project is just the beginning of my involvement with Extralit. The challenges of scientific data extraction are complex and evolving, and I'm committed to helping Extralit remain at the forefront of this field.

