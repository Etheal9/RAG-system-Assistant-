### Building a Biomedical RAG system with Docling and Weaviate

Docling is an open-source document understanding toolkit developed originally by IBM Research and now part of a broader community project. It’s designed to convert complex documents such as PDFs, DOCX, and images into structured, machine-readable formats with great applicability towards generative AI workflows and RAG applications. The Docling library handles layout, reading order, tables, code blocks, formulas, and other page elements, and offers a unified internal representation while offering the opportunity to run these models locally [1].

SmolDocling is a 256-million-parameter model released by IBM Research, that is trained to convert document images directly into a unified structured format called DocTags, capturing content, spatial layout, and document structure in one pass, rather than relying on separate OCR and layout pipelines [2] [3]. This end-to-end approach enables accurate extraction of tables, code, equations, charts, captions, and more from diverse document types, preserving both semantic and positional information for downstream RAG and AI tasks.

I spent some time experimenting with the Docling model and used it to build a structured workflow for processing PubMed articles, culminating in a RAG pipeline backed by Weaviate. In this blog post, I document my experiences with Docling and share code for implementing an end-to-end biomedical RAG system.

Building a Biomedical RAG System
The full code for this article can be found in this repository

Information extraction from unstructured documents is a field I’m particularly interested in, so I used this project as an opportunity to experiment with Docling and build a biomedical RAG system over PubMed articles. Beyond the system itself, my goal was to develop better intuition for working with vision–language models in document extraction settings and to more clearly understand their strengths and limitations