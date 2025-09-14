"""
Enhanced CLI interface for GenomeAI bioinformatics pipeline.
Includes pharmacogenomics, MTHFR, disease risk, and traits analysis.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

import typer
import pandas as pd

# Import core modules
from .qc import run_quality_control
from .align import align_reads
from .call_variants import call_variants
from .filter_variants import filter_variants
from .annotate import annotate_variants
from .rna import process_rna_seq
from .report import generate_reports

# Import enhanced analysis modules
from .pharmacogenomics import analyze_pharmacogenomics, generate_pharmacogenomics_report
from .mthfr import analyze_mthfr_variants, generate_mthfr_report
from .disease_risk import analyze_disease_risk_variants, generate_disease_risk_report
from .traits_ancestry import analyze_traits_and_ancestry, generate_traits_ancestry_report
from .enhanced_report import generate_enhanced_reports

# Import AI explanation modules
from .explain.build_index import build_faiss_index
from .explain.summarizer import explain_variants

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer(
    name="genomeai",
    help="Enhanced AI-powered genomics analysis pipeline with pharmacogenomics, MTHFR, disease risk, and traits analysis",
    add_completion=False
)


def load_config(config_file: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_file} not found, using defaults")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}")
        sys.exit(1)


@app.command()
def dna(
    reads1: str = typer.Argument(..., help="Path to R1 FASTQ file"),
    r2: Optional[str] = typer.Option(None, "--r2", help="Path to R2 FASTQ file (for paired-end)"),
    outdir: str = typer.Option("results", "--outdir", "-o", help="Output directory"),
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file"),
    threads: int = typer.Option(8, "--threads", "-t", help="Number of threads"),
    enhanced: bool = typer.Option(True, "--enhanced/--basic", help="Run enhanced analysis modules"),
    skip_qc: bool = typer.Option(False, "--skip-qc", help="Skip quality control"),
    skip_alignment: bool = typer.Option(False, "--skip-alignment", help="Skip alignment"),
    sample_name: str = typer.Option("sample", "--sample", help="Sample name")
):
    """
    Complete DNA analysis pipeline with enhanced genomics modules.
    
    Performs quality control, alignment, variant calling, annotation,
    and optional enhanced analysis (pharmacogenomics, MTHFR, disease risk, traits).
    """
    logger.info(f"Starting DNA analysis for {sample_name}")
    
    # Load configuration
    config = load_config(config_file)
    config['threads'] = threads
    
    # Create output directory
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Quality Control
        if not skip_qc:
            logger.info("Step 1: Quality control")
            qc_r1, qc_r2 = run_quality_control(reads1, r2, outdir_path, config)
        else:
            qc_r1, qc_r2 = reads1, r2
        
        # Step 2: Alignment
        if not skip_alignment:
            logger.info("Step 2: Read alignment")
            bam_file = align_reads(qc_r1, qc_r2, outdir_path, config, sample_name)
        else:
            # Assume BAM file exists
            bam_file = outdir_path / f"{sample_name}_aligned.bam"
        
        # Step 3: Variant calling
        logger.info("Step 3: Variant calling")
        vcf_file = call_variants(str(bam_file), outdir_path, config, sample_name)
        
        # Step 4: Variant filtering
        logger.info("Step 4: Variant filtering")
        filtered_vcf = filter_variants(str(vcf_file), outdir_path, config)
        
        # Step 5: Variant annotation
        logger.info("Step 5: Variant annotation")
        annotated_file = annotate_variants(str(filtered_vcf), outdir_path, config)
        
        # Step 6: Enhanced analysis modules (if enabled)
        enhanced_results = {}
        
        if enhanced and config.get('modules', {}).get('pharmacogenomics', True):
            logger.info("Step 6a: Pharmacogenomics analysis")
            pharmaco_results = analyze_pharmacogenomics(str(annotated_file), outdir_path, config)
            generate_pharmacogenomics_report(pharmaco_results, outdir_path)
            enhanced_results['pharmacogenomics'] = pharmaco_results
        
        if enhanced and config.get('modules', {}).get('mthfr', True):
            logger.info("Step 6b: MTHFR analysis")
            mthfr_results = analyze_mthfr_variants(str(annotated_file), outdir_path, config)
            generate_mthfr_report(mthfr_results, outdir_path)
            enhanced_results['mthfr'] = mthfr_results
        
        if enhanced and config.get('modules', {}).get('disease_risk', True):
            logger.info("Step 6c: Disease risk analysis")
            disease_results = analyze_disease_risk_variants(str(annotated_file), outdir_path, config)
            generate_disease_risk_report(disease_results, outdir_path)
            enhanced_results['disease_risk'] = disease_results
        
        if enhanced and config.get('modules', {}).get('traits_ancestry', True):
            logger.info("Step 6d: Traits and ancestry analysis")
            traits_results = analyze_traits_and_ancestry(str(annotated_file), outdir_path, config)
            generate_traits_ancestry_report(traits_results, outdir_path)
            enhanced_results['traits_ancestry'] = traits_results
        
        # Step 7: Generate reports
        logger.info("Step 7: Report generation")
        generate_reports(str(annotated_file), outdir_path, config)
        
        # Step 8: Generate comprehensive report (if enhanced modules were run)
        if enhanced and enhanced_results:
            logger.info("Step 8: Comprehensive report generation")
            generate_enhanced_reports(outdir_path, config, **enhanced_results)
        
        logger.info(f"DNA analysis completed successfully. Results in {outdir}")
        typer.echo(f"✅ DNA analysis completed! Results saved to: {outdir}")
        
        # Summary of outputs
        typer.echo("\n📁 Key Output Files:")
        typer.echo(f"   • Annotated variants: {annotated_file}")
        if enhanced_results:
            typer.echo(f"   • Pharmacogenomics report: {outdir}/pharmacogenomics/pharmacogenomics_report.md")
            typer.echo(f"   • MTHFR report: {outdir}/mthfr/mthfr_report.md")
            typer.echo(f"   • Disease risk report: {outdir}/disease_risk/disease_risk_report.md")
            typer.echo(f"   • Traits report: {outdir}/traits_ancestry/traits_ancestry_report.md")
            typer.echo(f"   • Comprehensive report: {outdir}/comprehensive_genomics_report.md")
        
    except Exception as e:
        logger.error(f"DNA analysis failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def drugs(
    variants_file: str = typer.Argument(..., help="Path to annotated variants file"),
    outdir: str = typer.Option("pharmacogenomics_results", "--outdir", "-o", help="Output directory"),
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file")
):
    """
    Analyze pharmacogenomics variants for drug-gene interactions.
    
    Analyzes CYP2D6, CYP2C19, TPMT, DPYD, and other pharmacogenes
    to predict drug metabolism and provide dosing recommendations.
    """
    logger.info("Starting pharmacogenomics analysis")
    
    # Load configuration
    config = load_config(config_file)
    
    # Create output directory
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run pharmacogenomics analysis
        results = analyze_pharmacogenomics(variants_file, outdir_path, config)
        
        # Generate report
        report_file = generate_pharmacogenomics_report(results, outdir_path)
        
        logger.info(f"Pharmacogenomics analysis completed. Report: {report_file}")
        typer.echo(f"✅ Pharmacogenomics analysis completed!")
        typer.echo(f"📄 Report: {report_file}")
        
        # Summary
        summary = results.get('summary', {})
        typer.echo(f"\n📊 Summary:")
        typer.echo(f"   • Genes analyzed: {summary.get('total_genes_analyzed', 0)}")
        typer.echo(f"   • High-risk findings: {len(summary.get('high_risk_findings', []))}")
        typer.echo(f"   • Drug interactions: {summary.get('drug_interactions_identified', 0)}")
        
    except Exception as e:
        logger.error(f"Pharmacogenomics analysis failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def mthfr(
    variants_file: str = typer.Argument(..., help="Path to annotated variants file"),
    outdir: str = typer.Option("mthfr_results", "--outdir", "-o", help="Output directory"),
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file")
):
    """
    Analyze MTHFR gene variants C677T and A1298C.
    
    Provides analysis of folate metabolism, homocysteine implications,
    and personalized recommendations for supplementation and lifestyle.
    """
    logger.info("Starting MTHFR analysis")
    
    # Load configuration
    config = load_config(config_file)
    
    # Create output directory
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run MTHFR analysis
        results = analyze_mthfr_variants(variants_file, outdir_path, config)
        
        # Generate report
        report_file = generate_mthfr_report(results, outdir_path)
        
        logger.info(f"MTHFR analysis completed. Report: {report_file}")
        typer.echo(f"✅ MTHFR analysis completed!")
        typer.echo(f"📄 Report: {report_file}")
        
        # Summary
        combined = results.get('combined_analysis', {})
        typer.echo(f"\n📊 Summary:")
        typer.echo(f"   • Combined genotype: {combined.get('combined_genotype', 'Unknown')}")
        typer.echo(f"   • Risk level: {combined.get('risk_level', 'Unknown')}")
        typer.echo(f"   • Variants present: {'Yes' if combined.get('variants_present', False) else 'No'}")
        
    except Exception as e:
        logger.error(f"MTHFR analysis failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def disease_risk(
    variants_file: str = typer.Argument(..., help="Path to annotated variants file"),
    outdir: str = typer.Option("disease_risk_results", "--outdir", "-o", help="Output directory"),
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file")
):
    """
    Analyze disease risk variants (BRCA1/2, APOE, HFE, etc.).
    
    Analyzes variants in genes associated with cancer predisposition,
    Alzheimer's disease, hemochromatosis, and other genetic conditions.
    """
    logger.info("Starting disease risk analysis")
    
    # Load configuration
    config = load_config(config_file)
    
    # Create output directory
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run disease risk analysis
        results = analyze_disease_risk_variants(variants_file, outdir_path, config)
        
        # Generate report
        report_file = generate_disease_risk_report(results, outdir_path)
        
        logger.info(f"Disease risk analysis completed. Report: {report_file}")
        typer.echo(f"✅ Disease risk analysis completed!")
        typer.echo(f"📄 Report: {report_file}")
        
        # Summary
        summary = results.get('summary', {})
        typer.echo(f"\n📊 Summary:")
        typer.echo(f"   • High-risk findings: {len(summary.get('high_risk_findings', []))}")
        typer.echo(f"   • Actionable findings: {summary.get('actionable_findings', 0)}")
        typer.echo(f"   • Genes analyzed: {summary.get('total_genes_analyzed', 0)}")
        
    except Exception as e:
        logger.error(f"Disease risk analysis failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def traits(
    variants_file: str = typer.Argument(..., help="Path to annotated variants file"),
    outdir: str = typer.Option("traits_results", "--outdir", "-o", help="Output directory"),
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file")
):
    """
    Analyze physical traits, nutritional genomics, and ancestry markers.
    
    Analyzes variants for eye color, hair color, lactose tolerance,
    caffeine metabolism, and ancestry informative markers.
    """
    logger.info("Starting traits and ancestry analysis")
    
    # Load configuration
    config = load_config(config_file)
    
    # Create output directory
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run traits analysis
        results = analyze_traits_and_ancestry(variants_file, outdir_path, config)
        
        # Generate report
        report_file = generate_traits_ancestry_report(results, outdir_path)
        
        logger.info(f"Traits analysis completed. Report: {report_file}")
        typer.echo(f"✅ Traits and ancestry analysis completed!")
        typer.echo(f"📄 Report: {report_file}")
        
        # Summary
        summary = results.get('summary', {})
        typer.echo(f"\n📊 Summary:")
        typer.echo(f"   • Physical traits: {summary.get('traits_analyzed', 0)}")
        typer.echo(f"   • Nutritional markers: {summary.get('nutritional_markers', 0)}")
        typer.echo(f"   • Actionable findings: {len(summary.get('actionable_findings', []))}")
        
    except Exception as e:
        logger.error(f"Traits analysis failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def run_all(
    reads1: str = typer.Argument(..., help="Path to R1 FASTQ file"),
    r2: Optional[str] = typer.Option(None, "--r2", help="Path to R2 FASTQ file (for paired-end)"),
    outdir: str = typer.Option("complete_analysis", "--outdir", "-o", help="Output directory"),
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file"),
    threads: int = typer.Option(8, "--threads", "-t", help="Number of threads"),
    sample_name: str = typer.Option("sample", "--sample", help="Sample name"),
    modules: str = typer.Option("all", "--modules", help="Modules to run: all,basic,pharmaco,mthfr,disease,traits")
):
    """
    Run complete genomics analysis pipeline with all enhanced modules.
    
    Performs the full pipeline including DNA analysis, pharmacogenomics,
    MTHFR analysis, disease risk assessment, and traits analysis.
    """
    logger.info(f"Starting complete analysis for {sample_name}")
    
    # Parse modules
    if modules == "all":
        run_modules = ["basic", "pharmaco", "mthfr", "disease", "traits"]
    else:
        run_modules = [m.strip() for m in modules.split(",")]
    
    # Load configuration
    config = load_config(config_file)
    config['threads'] = threads
    
    # Create output directory
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1-5: Core DNA analysis pipeline
        logger.info("Running core DNA analysis pipeline...")
        
        # Quality Control
        logger.info("Step 1: Quality control")
        qc_r1, qc_r2 = run_quality_control(reads1, r2, outdir_path, config)
        
        # Alignment
        logger.info("Step 2: Read alignment")
        bam_file = align_reads(qc_r1, qc_r2, outdir_path, config, sample_name)
        
        # Variant calling
        logger.info("Step 3: Variant calling")
        vcf_file = call_variants(str(bam_file), outdir_path, config, sample_name)
        
        # Variant filtering
        logger.info("Step 4: Variant filtering")
        filtered_vcf = filter_variants(str(vcf_file), outdir_path, config)
        
        # Variant annotation
        logger.info("Step 5: Variant annotation")
        annotated_file = annotate_variants(str(filtered_vcf), outdir_path, config)
        
        # Enhanced analysis modules
        enhanced_results = {}
        
        if "pharmaco" in run_modules:
            logger.info("Step 6a: Pharmacogenomics analysis")
            pharmaco_results = analyze_pharmacogenomics(str(annotated_file), outdir_path, config)
            generate_pharmacogenomics_report(pharmaco_results, outdir_path)
            enhanced_results['pharmacogenomics'] = pharmaco_results
        
        if "mthfr" in run_modules:
            logger.info("Step 6b: MTHFR analysis")
            mthfr_results = analyze_mthfr_variants(str(annotated_file), outdir_path, config)
            generate_mthfr_report(mthfr_results, outdir_path)
            enhanced_results['mthfr'] = mthfr_results
        
        if "disease" in run_modules:
            logger.info("Step 6c: Disease risk analysis")
            disease_results = analyze_disease_risk_variants(str(annotated_file), outdir_path, config)
            generate_disease_risk_report(disease_results, outdir_path)
            enhanced_results['disease_risk'] = disease_results
        
        if "traits" in run_modules:
            logger.info("Step 6d: Traits and ancestry analysis")
            traits_results = analyze_traits_and_ancestry(str(annotated_file), outdir_path, config)
            generate_traits_ancestry_report(traits_results, outdir_path)
            enhanced_results['traits_ancestry'] = traits_results
        
        # Generate reports
        logger.info("Step 7: Report generation")
        generate_reports(str(annotated_file), outdir_path, config)
        
        # Generate comprehensive report
        if enhanced_results:
            logger.info("Step 8: Comprehensive report generation")
            generate_enhanced_reports(outdir_path, config, **enhanced_results)
        
        logger.info(f"Complete analysis finished successfully. Results in {outdir}")
        typer.echo(f"🎉 Complete genomics analysis finished!")
        typer.echo(f"📁 All results saved to: {outdir}")
        
        # Summary of all outputs
        typer.echo("\n📋 Analysis Summary:")
        typer.echo(f"   • Core pipeline: ✅ Completed")
        if "pharmaco" in run_modules:
            typer.echo(f"   • Pharmacogenomics: ✅ Completed")
        if "mthfr" in run_modules:
            typer.echo(f"   • MTHFR analysis: ✅ Completed")
        if "disease" in run_modules:
            typer.echo(f"   • Disease risk: ✅ Completed")
        if "traits" in run_modules:
            typer.echo(f"   • Traits & ancestry: ✅ Completed")
        
        typer.echo(f"\n📄 Key Reports:")
        if enhanced_results:
            typer.echo(f"   • Comprehensive report: {outdir}/comprehensive_genomics_report.md")
        typer.echo(f"   • Individual module reports available in respective subdirectories")
        
    except Exception as e:
        logger.error(f"Complete analysis failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def rna_only(
    reads1: str = typer.Argument(..., help="Path to R1 RNA-seq FASTQ file"),
    r2: Optional[str] = typer.Option(None, "--r2", help="Path to R2 FASTQ file (for paired-end)"),
    outdir: str = typer.Option("rna_results", "--outdir", "-o", help="Output directory"),
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file"),
    threads: int = typer.Option(8, "--threads", "-t", help="Number of threads"),
    sample_name: str = typer.Option("sample", "--sample", help="Sample name")
):
    """
    RNA-seq only analysis pipeline.
    
    Performs quality control, alignment to transcriptome, and quantification
    of gene expression using Salmon.
    """
    logger.info(f"Starting RNA-seq analysis for {sample_name}")
    
    # Load configuration
    config = load_config(config_file)
    config['threads'] = threads
    
    # Create output directory
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Quality Control
        logger.info("Step 1: Quality control")
        qc_r1, qc_r2 = run_quality_control(reads1, r2, outdir_path, config)
        
        # RNA-seq processing
        logger.info("Step 2: RNA-seq quantification")
        results = process_rna_seq(qc_r1, qc_r2, outdir_path, config, sample_name)
        
        logger.info(f"RNA-seq analysis completed. Results in {outdir}")
        typer.echo(f"✅ RNA-seq analysis completed!")
        typer.echo(f"📁 Results saved to: {outdir}")
        typer.echo(f"📄 Gene expression: {results.get('quant_file', 'quant.sf')}")
        
    except Exception as e:
        logger.error(f"RNA-seq analysis failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def explain(
    variants_file: str = typer.Argument(..., help="Path to annotated variants file"),
    outdir: str = typer.Option("explanations", "--outdir", "-o", help="Output directory"),
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file"),
    max_variants: int = typer.Option(50, "--max-variants", help="Maximum variants to explain")
):
    """
    Generate AI explanations for genetic variants.
    
    Uses FAISS similarity search and local LLM to provide detailed
    explanations of genetic variants and their clinical significance.
    """
    logger.info("Starting variant explanation generation")
    
    # Load configuration
    config = load_config(config_file)
    config['explain']['max_variants_to_explain'] = max_variants
    
    # Create output directory
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Generate explanations
        explanations = explain_variants(variants_file, outdir_path, config)
        
        logger.info(f"Variant explanations completed. Results in {outdir}")
        typer.echo(f"✅ Variant explanations generated!")
        typer.echo(f"📁 Results saved to: {outdir}")
        typer.echo(f"📄 Explanations: {len(explanations)} variants explained")
        
    except Exception as e:
        logger.error(f"Variant explanation failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def build_index(
    clinvar_file: str = typer.Argument(..., help="Path to ClinVar summary file"),
    outdir: str = typer.Option("faiss_index", "--outdir", "-o", help="Output directory for index"),
    config_file: str = typer.Option("config.yaml", "--config", "-c", help="Configuration file")
):
    """
    Build FAISS index from ClinVar data for variant explanations.
    
    Creates a searchable index of ClinVar variants for similarity-based
    variant explanation and clinical significance lookup.
    """
    logger.info("Building FAISS index from ClinVar data")
    
    # Load configuration
    config = load_config(config_file)
    
    # Create output directory
    outdir_path = Path(outdir)
    outdir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Build index
        index_info = build_faiss_index(clinvar_file, outdir_path, config)
        
        logger.info(f"FAISS index built successfully. Index in {outdir}")
        typer.echo(f"✅ FAISS index built successfully!")
        typer.echo(f"📁 Index saved to: {outdir}")
        typer.echo(f"📊 Index contains: {index_info.get('num_variants', 0)} variants")
        
    except Exception as e:
        logger.error(f"Index building failed: {e}")
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """Show GenomeAI version information."""
    typer.echo("GenomeAI Enhanced Genomics Pipeline v1.0.0")
    typer.echo("Enhanced with pharmacogenomics, MTHFR, disease risk, and traits analysis")
    typer.echo("For more information, visit: https://github.com/genomeai/genomeai")


if __name__ == "__main__":
    app()