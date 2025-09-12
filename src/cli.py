"""
GenomeAI CLI interface using Typer.
Provides commands for DNA analysis, RNA-only analysis, and explanation generation.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml

from . import __version__
from .qc import run_qc
from .align import run_alignment
from .call_variants import call_variants
from .filter_variants import filter_variants
from .annotate import annotate_variants
from .rna import process_rna
from .report import generate_report
from .explain.build_index import build_clinvar_index
from .explain.retriever import retrieve_similar_variants
from .explain.summarizer import summarize_variants

app = typer.Typer(help="GenomeAI: AI-powered genomics analysis pipeline")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file {config_path} not found")
        sys.exit(1)


@app.command()
def dna(
    r1: str = typer.Argument(..., help="Forward reads FASTQ file"),
    r2: Optional[str] = typer.Option(None, "--r2", help="Reverse reads FASTQ file"),
    outdir: str = typer.Option("output", "--outdir", help="Output directory"),
    config: str = typer.Option("config.yaml", "--config", help="Configuration file"),
    reference: Optional[str] = typer.Option(None, "--reference", help="Reference genome path"),
    platform: str = typer.Option("illumina", "--platform", help="Sequencing platform (illumina/nanopore)"),
):
    """Run complete DNA analysis pipeline."""
    logger.info(f"Starting GenomeAI v{__version__} DNA analysis")
    
    config_data = load_config(config)
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    # QC and trimming
    logger.info("Running quality control and trimming")
    qc_output = run_qc(r1, r2, outdir_path, config_data)
    
    # Alignment
    logger.info("Running read alignment")
    bam_file = run_alignment(qc_output, outdir_path, reference, platform, config_data)
    
    # Variant calling
    logger.info("Calling variants")
    vcf_file = call_variants(bam_file, outdir_path, reference, config_data)
    
    # Variant filtering
    logger.info("Filtering variants")
    filtered_vcf = filter_variants(vcf_file, outdir_path, config_data)
    
    # Variant annotation
    logger.info("Annotating variants")
    annotated_file = annotate_variants(filtered_vcf, outdir_path, config_data)
    
    # Generate report
    logger.info("Generating report")
    generate_report(annotated_file, None, outdir_path, config_data)
    
    logger.info(f"DNA analysis complete. Results in {outdir}")


@app.command()
def rna_only(
    r1: str = typer.Argument(..., help="Forward RNA-seq reads"),
    r2: Optional[str] = typer.Option(None, "--r2", help="Reverse RNA-seq reads"),
    outdir: str = typer.Option("output_rna", "--outdir", help="Output directory"),
    config: str = typer.Option("config.yaml", "--config", help="Configuration file"),
):
    """Run RNA-seq only analysis."""
    logger.info(f"Starting GenomeAI v{__version__} RNA-seq analysis")
    
    config_data = load_config(config)
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    # Process RNA-seq
    logger.info("Processing RNA-seq data")
    rna_output = process_rna(r1, r2, outdir_path, config_data)
    
    # Generate RNA-only report
    logger.info("Generating RNA report")
    generate_report(None, rna_output, outdir_path, config_data)
    
    logger.info(f"RNA-seq analysis complete. Results in {outdir}")


@app.command()
def explain(
    variants_file: str = typer.Argument(..., help="Annotated variants parquet file"),
    outdir: str = typer.Option("explanation_output", "--outdir", help="Output directory"),
    config: str = typer.Option("config.yaml", "--config", help="Configuration file"),
    rebuild_index: bool = typer.Option(False, "--rebuild-index", help="Rebuild FAISS index"),
):
    """Generate AI explanations for variants."""
    logger.info(f"Starting GenomeAI v{__version__} explanation generation")
    
    config_data = load_config(config)
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    # Build or load index
    if rebuild_index:
        logger.info("Building ClinVar FAISS index")
        build_clinvar_index(config_data)
    
    # Retrieve similar variants and generate explanations
    logger.info("Generating AI explanations")
    explanations = summarize_variants(variants_file, config_data)
    
    # Generate explanation report
    logger.info("Generating explanation report")
    generate_report(variants_file, None, outdir_path, config_data, explanations)
    
    logger.info(f"Explanation generation complete. Results in {outdir}")


@app.command()
def build_index(
    config: str = typer.Option("config.yaml", "--config", help="Configuration file"),
):
    """Build ClinVar FAISS index for similarity search."""
    logger.info("Building ClinVar FAISS index")
    config_data = load_config(config)
    build_clinvar_index(config_data)
    logger.info("Index building complete")


@app.command()
def version():
    """Show GenomeAI version."""
    typer.echo(f"GenomeAI v{__version__}")


if __name__ == "__main__":
    app()