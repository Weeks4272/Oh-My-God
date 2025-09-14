GenomeAI Development TODO
Project Structure
src/cli.py - Main CLI interface using Typer
src/qc.py - Quality control and trimming with fastp
src/align.py - Read alignment (bwa-mem2, minimap2)
src/call_variants.py - Variant calling with FreeBayes
src/filter_variants.py - Variant filtering
src/annotate.py - Variant annotation with VEP
src/rna.py - RNA-seq processing with Salmon
src/report.py - Report generation
src/explain/build_index.py - FAISS index building
src/explain/retriever.py - Similarity search
src/explain/summarizer.py - LLM summarization
src/explain/templates.py - Prompt templates
config.yaml - Configuration file
requirements.txt - Python dependencies
environment.yml - Conda environment
Dockerfile - Container setup
README.md - Documentation
Implementation Status
[ ] All modules implemented
[ ] Configuration setup
[ ] Dependencies defined
[ ] Docker configuration
[ ] Documentation complete