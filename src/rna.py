"""
RNA-seq processing module using Salmon for quantification.
"""

import logging
import subprocess
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


def process_rna(
    r1: str, 
    r2: Optional[str], 
    outdir: Path, 
    config: Dict[str, Any]
) -> str:
    """
    Process RNA-seq data using Salmon quantification.
    
    Args:
        r1: Forward RNA-seq reads
        r2: Reverse RNA-seq reads (optional)
        outdir: Output directory
        config: Configuration dictionary
        
    Returns:
        Path to quantification results directory
    """
    logger.info("Starting RNA-seq processing with Salmon")
    
    rna_dir = outdir / "rna_quant"
    rna_dir.mkdir(exist_ok=True)
    
    # Get or build Salmon index
    salmon_index = _get_salmon_index(config)
    
    # Run Salmon quantification
    quant_dir = _run_salmon_quantification(r1, r2, salmon_index, rna_dir, config)
    
    # Process quantification results
    _process_salmon_output(quant_dir, rna_dir, config)
    
    return str(rna_dir)


def _get_salmon_index(config: Dict[str, Any]) -> str:
    """Get or build Salmon transcriptome index."""
    
    rna_config = config.get("rna", {})
    salmon_config = rna_config.get("salmon", {})
    
    # Check if index already exists
    index_path = salmon_config.get("index_path")
    if index_path and Path(index_path).exists():
        logger.info(f"Using existing Salmon index: {index_path}")
        return index_path
    
    # Build new index if transcriptome is provided
    transcriptome_fasta = salmon_config.get("transcriptome_fasta")
    if not transcriptome_fasta:
        raise ValueError("Salmon index path or transcriptome FASTA must be provided in config")
    
    if not Path(transcriptome_fasta).exists():
        raise FileNotFoundError(f"Transcriptome FASTA not found: {transcriptome_fasta}")
    
    # Create index directory
    index_dir = Path("salmon_index")
    index_dir.mkdir(exist_ok=True)
    
    logger.info("Building Salmon transcriptome index")
    
    cmd = [
        "salmon", "index",
        "-t", transcriptome_fasta,
        "-i", str(index_dir),
        "--type", "quasi"
    ]
    
    # Add k-mer length if specified
    kmer_len = salmon_config.get("kmer_length", 31)
    cmd.extend(["-k", str(kmer_len)])
    
    # Additional index parameters
    index_params = salmon_config.get("index_params", [])
    cmd.extend(index_params)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Salmon index built successfully")
        return str(index_dir)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Salmon index building failed: {e.stderr}")
        raise RuntimeError(f"Salmon index building failed: {e.stderr}")


def _run_salmon_quantification(
    r1: str, 
    r2: Optional[str], 
    salmon_index: str, 
    rna_dir: Path, 
    config: Dict[str, Any]
) -> Path:
    """Run Salmon quantification."""
    
    logger.info("Running Salmon quantification")
    
    quant_dir = rna_dir / "salmon_quant"
    
    rna_config = config.get("rna", {})
    salmon_config = rna_config.get("salmon", {})
    
    cmd = [
        "salmon", "quant",
        "-i", salmon_index,
        "-l", "A",  # Automatic library type detection
        "-1", r1,
        "-o", str(quant_dir),
        "--validateMappings",
        "--gcBias",
        "--seqBias"
    ]
    
    if r2:
        cmd.extend(["-2", r2])
    
    # Add threading
    threads = config.get("threads", 4)
    cmd.extend(["-p", str(threads)])
    
    # Bootstrap samples for uncertainty quantification
    bootstrap_samples = salmon_config.get("bootstrap_samples", 100)
    cmd.extend(["--numBootstraps", str(bootstrap_samples)])
    
    # Additional Salmon parameters
    additional_params = salmon_config.get("additional_params", [])
    cmd.extend(additional_params)
    
    logger.info(f"Running Salmon command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Salmon quantification completed successfully")
        
        # Log mapping statistics
        _log_salmon_stats(quant_dir)
        
        return quant_dir
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Salmon quantification failed: {e.stderr}")
        raise RuntimeError(f"Salmon quantification failed: {e.stderr}")
    except FileNotFoundError:
        logger.error("Salmon not found. Please install Salmon.")
        raise RuntimeError("Salmon not installed")


def _log_salmon_stats(quant_dir: Path) -> None:
    """Log Salmon quantification statistics."""
    
    try:
        # Read mapping info from logs
        log_file = quant_dir / "logs" / "salmon_quant.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_content = f.read()
                
                # Extract key statistics
                lines = log_content.split('\n')
                for line in lines:
                    if "Mapping rate" in line:
                        logger.info(f"Salmon mapping rate: {line.strip()}")
                    elif "successfully aligned" in line:
                        logger.info(f"Salmon alignment: {line.strip()}")
        
        # Read quantification summary
        quant_file = quant_dir / "quant.sf"
        if quant_file.exists():
            df = pd.read_csv(quant_file, sep='\t')
            total_transcripts = len(df)
            expressed_transcripts = len(df[df['TPM'] > 1])
            
            logger.info(f"Total transcripts: {total_transcripts}")
            logger.info(f"Expressed transcripts (TPM > 1): {expressed_transcripts}")
            logger.info(f"Expression rate: {(expressed_transcripts/total_transcripts)*100:.2f}%")
            
    except Exception as e:
        logger.warning(f"Could not parse Salmon statistics: {e}")


def _process_salmon_output(quant_dir: Path, rna_dir: Path, config: Dict[str, Any]) -> None:
    """Process and summarize Salmon quantification output."""
    
    logger.info("Processing Salmon quantification results")
    
    try:
        # Read quantification results
        quant_file = quant_dir / "quant.sf"
        if not quant_file.exists():
            logger.error("Salmon quantification file not found")
            return
        
        df = pd.read_csv(quant_file, sep='\t')
        
        # Add gene-level summarization if transcript-to-gene mapping is available
        tx2gene_file = config.get("rna", {}).get("tx2gene_mapping")
        if tx2gene_file and Path(tx2gene_file).exists():
            df = _summarize_to_gene_level(df, tx2gene_file)
        
        # Create expression summary
        summary = _create_expression_summary(df)
        
        # Save processed results
        processed_file = rna_dir / "expression_summary.tsv"
        df.to_csv(processed_file, sep='\t', index=False)
        
        # Save top expressed genes/transcripts
        top_expressed = df.nlargest(100, 'TPM')
        top_file = rna_dir / "top_expressed.tsv"
        top_expressed.to_csv(top_file, sep='\t', index=False)
        
        # Save summary statistics
        summary_file = rna_dir / "expression_stats.json"
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("RNA-seq processing completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to process Salmon output: {e}")


def _summarize_to_gene_level(df: pd.DataFrame, tx2gene_file: str) -> pd.DataFrame:
    """Summarize transcript-level quantification to gene level."""
    
    logger.info("Summarizing to gene level")
    
    try:
        # Read transcript-to-gene mapping
        tx2gene = pd.read_csv(tx2gene_file, sep='\t', header=None, names=['transcript_id', 'gene_id'])
        
        # Merge with quantification data
        merged = df.merge(tx2gene, left_on='Name', right_on='transcript_id', how='left')
        
        # Sum TPM and NumReads by gene
        gene_summary = merged.groupby('gene_id').agg({
            'TPM': 'sum',
            'NumReads': 'sum',
            'Length': 'mean'  # Average transcript length per gene
        }).reset_index()
        
        gene_summary = gene_summary.rename(columns={'gene_id': 'Name'})
        
        logger.info(f"Summarized {len(df)} transcripts to {len(gene_summary)} genes")
        return gene_summary
        
    except Exception as e:
        logger.warning(f"Gene-level summarization failed: {e}")
        return df


def _create_expression_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Create expression summary statistics."""
    
    summary = {
        'total_features': len(df),
        'expressed_features_tpm1': len(df[df['TPM'] >= 1]),
        'expressed_features_tpm5': len(df[df['TPM'] >= 5]),
        'highly_expressed_features': len(df[df['TPM'] >= 100]),
        'median_tpm': float(df['TPM'].median()),
        'mean_tpm': float(df['TPM'].mean()),
        'total_reads': int(df['NumReads'].sum()) if 'NumReads' in df.columns else 0
    }
    
    # Expression percentiles
    summary['tpm_percentiles'] = {
        '25th': float(df['TPM'].quantile(0.25)),
        '50th': float(df['TPM'].quantile(0.50)),
        '75th': float(df['TPM'].quantile(0.75)),
        '90th': float(df['TPM'].quantile(0.90)),
        '95th': float(df['TPM'].quantile(0.95))
    }
    
    return summary


def differential_expression_analysis(
    sample_files: list, 
    conditions: list, 
    outdir: Path, 
    config: Dict[str, Any]
) -> str:
    """
    Perform differential expression analysis (placeholder for future implementation).
    
    Args:
        sample_files: List of quantification files
        conditions: List of condition labels
        outdir: Output directory
        config: Configuration dictionary
        
    Returns:
        Path to differential expression results
    """
    logger.info("Differential expression analysis not implemented in MVP")
    logger.info("This would use DESeq2 or edgeR for multi-sample comparison")
    
    # Placeholder implementation
    de_dir = outdir / "differential_expression"
    de_dir.mkdir(exist_ok=True)
    
    # In a full implementation, this would:
    # 1. Combine multiple sample quantifications
    # 2. Normalize expression values
    # 3. Perform statistical testing (DESeq2/edgeR)
    # 4. Apply multiple testing correction
    # 5. Generate volcano plots and heatmaps
    
    return str(de_dir)


def create_expression_plots(rna_dir: Path, config: Dict[str, Any]) -> None:
    """Create expression visualization plots (placeholder)."""
    
    logger.info("Expression plotting not implemented in MVP")
    
    # This would create:
    # 1. TPM distribution histograms
    # 2. Sample correlation plots
    # 3. PCA plots for multiple samples
    # 4. Expression heatmaps for top genes
    
    pass