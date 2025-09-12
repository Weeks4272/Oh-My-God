"""
Variant annotation module using Ensembl VEP with ClinVar and gnomAD databases.
"""

import logging
import subprocess
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def annotate_variants(
    vcf_file: str, 
    outdir: Path, 
    config: Dict[str, Any]
) -> str:
    """
    Annotate variants using Ensembl VEP with multiple databases.
    
    Args:
        vcf_file: Path to filtered VCF file
        outdir: Output directory
        config: Configuration dictionary
        
    Returns:
        Path to annotated parquet file
    """
    logger.info("Starting variant annotation with VEP")
    
    annotation_dir = outdir / "annotation"
    annotation_dir.mkdir(exist_ok=True)
    
    # VEP output files
    vep_output = annotation_dir / "variants_vep.vcf"
    vep_tab_output = annotation_dir / "variants_vep.txt"
    
    # Run VEP annotation
    _run_vep_annotation(vcf_file, vep_output, vep_tab_output, config)
    
    # Convert to structured format and add additional annotations
    parquet_file = _process_vep_output(vep_tab_output, annotation_dir, config)
    
    return parquet_file


def _run_vep_annotation(
    vcf_file: str, 
    vep_output: Path, 
    vep_tab_output: Path, 
    config: Dict[str, Any]
) -> None:
    """Run Ensembl VEP annotation."""
    
    vep_config = config.get("annotation", {}).get("vep", {})
    
    # Base VEP command
    cmd = [
        "vep",
        "--input_file", vcf_file,
        "--output_file", str(vep_output),
        "--tab",
        "--everything",  # Include all available annotations
        "--force_overwrite",
        "--offline",  # Use offline cache
        "--format", "vcf",
        "--vcf",  # Output VCF format as well
    ]
    
    # Add cache directory if specified
    cache_dir = vep_config.get("cache_dir")
    if cache_dir:
        cmd.extend(["--cache", "--dir_cache", cache_dir])
    
    # Add species and assembly
    species = vep_config.get("species", "homo_sapiens")
    assembly = vep_config.get("assembly", "GRCh38")
    cmd.extend(["--species", species, "--assembly", assembly])
    
    # Add database plugins
    plugins = vep_config.get("plugins", [])
    for plugin in plugins:
        cmd.extend(["--plugin", plugin])
    
    # Add custom annotations
    custom_annotations = vep_config.get("custom", [])
    for custom in custom_annotations:
        cmd.extend(["--custom", custom])
    
    # Add fields to include
    fields = vep_config.get("fields", [
        "Uploaded_variation", "Location", "Allele", "Gene", "Feature", 
        "Feature_type", "Consequence", "cDNA_position", "CDS_position", 
        "Protein_position", "Amino_acids", "Codons", "Existing_variation", 
        "IMPACT", "DISTANCE", "STRAND", "FLAGS"
    ])
    
    if fields:
        cmd.extend(["--fields", ",".join(fields)])
    
    # Additional VEP parameters
    additional_params = vep_config.get("additional_params", [])
    cmd.extend(additional_params)
    
    logger.info(f"Running VEP command: {' '.join(cmd)}")
    
    try:
        # Also create tab-delimited output
        tab_cmd = cmd.copy()
        tab_cmd[tab_cmd.index("--output_file") + 1] = str(vep_tab_output)
        if "--vcf" in tab_cmd:
            tab_cmd.remove("--vcf")
        
        result = subprocess.run(tab_cmd, check=True, capture_output=True, text=True)
        logger.info("VEP annotation completed successfully")
        logger.debug(f"VEP output: {result.stdout}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"VEP annotation failed: {e.stderr}")
        raise RuntimeError(f"VEP annotation failed: {e.stderr}")
    except FileNotFoundError:
        logger.error("VEP not found. Please install Ensembl VEP.")
        raise RuntimeError("VEP not installed")


def _process_vep_output(
    vep_tab_file: Path, 
    annotation_dir: Path, 
    config: Dict[str, Any]
) -> str:
    """Process VEP tab output and convert to parquet format with additional annotations."""
    
    logger.info("Processing VEP output and adding additional annotations")
    
    try:
        # Read VEP output
        df = pd.read_csv(vep_tab_file, sep='\t', comment='#', low_memory=False)
        
        if df.empty:
            logger.warning("No variants found in VEP output")
            # Create empty parquet file
            empty_df = pd.DataFrame()
            parquet_file = annotation_dir / "variants_annotated.parquet"
            empty_df.to_parquet(parquet_file)
            return str(parquet_file)
        
        logger.info(f"Processing {len(df)} annotated variants")
        
        # Add ClinVar annotations if available
        df = _add_clinvar_annotations(df, config)
        
        # Add gnomAD frequencies if available
        df = _add_gnomad_annotations(df, config)
        
        # Add custom scoring
        df = _add_variant_scoring(df, config)
        
        # Clean and standardize columns
        df = _clean_annotations(df)
        
        # Save to parquet format
        parquet_file = annotation_dir / "variants_annotated.parquet"
        df.to_parquet(parquet_file, index=False)
        
        # Also save as TSV for human readability
        tsv_file = annotation_dir / "variants_annotated.tsv"
        df.to_csv(tsv_file, sep='\t', index=False)
        
        logger.info(f"Annotation processing complete. Output saved to {parquet_file}")
        return str(parquet_file)
        
    except Exception as e:
        logger.error(f"Failed to process VEP output: {e}")
        raise RuntimeError(f"VEP output processing failed: {e}")


def _add_clinvar_annotations(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Add ClinVar pathogenicity annotations."""
    
    logger.info("Adding ClinVar annotations")
    
    # This would typically involve querying ClinVar database
    # For now, we'll add placeholder columns that would be populated
    # by actual ClinVar data in a production system
    
    df['ClinVar_Significance'] = None
    df['ClinVar_ReviewStatus'] = None
    df['ClinVar_Conditions'] = None
    df['ClinVar_ID'] = None
    
    # In a real implementation, this would:
    # 1. Query ClinVar database using variant coordinates
    # 2. Match variants by position and alleles
    # 3. Add pathogenicity classifications
    
    return df


def _add_gnomad_annotations(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Add gnomAD population frequency annotations."""
    
    logger.info("Adding gnomAD frequency annotations")
    
    # Add gnomAD frequency columns
    df['gnomAD_AF'] = None  # Overall allele frequency
    df['gnomAD_AF_AFR'] = None  # African/African American
    df['gnomAD_AF_AMR'] = None  # Latino/Admixed American
    df['gnomAD_AF_ASJ'] = None  # Ashkenazi Jewish
    df['gnomAD_AF_EAS'] = None  # East Asian
    df['gnomAD_AF_FIN'] = None  # Finnish
    df['gnomAD_AF_NFE'] = None  # Non-Finnish European
    df['gnomAD_AF_SAS'] = None  # South Asian
    
    # In a real implementation, this would:
    # 1. Query gnomAD database or VCF files
    # 2. Extract population-specific frequencies
    # 3. Add quality metrics and coverage information
    
    return df


def _add_variant_scoring(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Add custom variant scoring and prioritization."""
    
    logger.info("Adding variant scoring")
    
    # Initialize scoring columns
    df['Pathogenicity_Score'] = 0.0
    df['Clinical_Significance'] = 'Unknown'
    df['Priority_Rank'] = 0
    
    # Simple scoring based on consequence and frequency
    if 'Consequence' in df.columns:
        # High impact consequences
        high_impact = ['transcript_ablation', 'splice_acceptor_variant', 
                      'splice_donor_variant', 'stop_gained', 'frameshift_variant']
        
        moderate_impact = ['missense_variant', 'protein_altering_variant', 
                          'inframe_deletion', 'inframe_insertion']
        
        for idx, row in df.iterrows():
            consequence = str(row.get('Consequence', ''))
            score = 0.0
            
            # Score based on consequence severity
            if any(cons in consequence for cons in high_impact):
                score += 0.8
                df.at[idx, 'Clinical_Significance'] = 'Likely Pathogenic'
            elif any(cons in consequence for cons in moderate_impact):
                score += 0.5
                df.at[idx, 'Clinical_Significance'] = 'Uncertain Significance'
            else:
                score += 0.1
                df.at[idx, 'Clinical_Significance'] = 'Likely Benign'
            
            # Adjust score based on frequency (if available)
            gnomad_af = row.get('gnomAD_AF')
            if gnomad_af is not None and gnomad_af > 0.01:  # Common variant
                score *= 0.1  # Reduce pathogenicity score
            
            df.at[idx, 'Pathogenicity_Score'] = score
    
    # Rank variants by score
    df['Priority_Rank'] = df['Pathogenicity_Score'].rank(method='dense', ascending=False)
    
    return df


def _clean_annotations(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize annotation columns."""
    
    logger.info("Cleaning annotation data")
    
    # Standardize column names
    column_mapping = {
        'Uploaded_variation': 'Variant_ID',
        'Location': 'Genomic_Position',
        'Existing_variation': 'dbSNP_ID'
    }
    
    df = df.rename(columns=column_mapping)
    
    # Fill missing values
    string_columns = df.select_dtypes(include=['object']).columns
    df[string_columns] = df[string_columns].fillna('.')
    
    numeric_columns = df.select_dtypes(include=['number']).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Remove duplicate variants (keep highest scoring)
    if 'Variant_ID' in df.columns and 'Pathogenicity_Score' in df.columns:
        df = df.sort_values('Pathogenicity_Score', ascending=False)
        df = df.drop_duplicates(subset=['Variant_ID'], keep='first')
    
    return df


def create_annotation_summary(parquet_file: str, outdir: Path) -> Dict[str, Any]:
    """Create summary statistics for annotated variants."""
    
    logger.info("Creating annotation summary")
    
    try:
        df = pd.read_parquet(parquet_file)
        
        summary = {
            'total_variants': len(df),
            'consequence_counts': {},
            'impact_distribution': {},
            'clinical_significance_counts': {},
            'top_genes': []
        }
        
        # Consequence type distribution
        if 'Consequence' in df.columns:
            consequence_counts = df['Consequence'].value_counts().head(10).to_dict()
            summary['consequence_counts'] = consequence_counts
        
        # Impact distribution
        if 'IMPACT' in df.columns:
            impact_counts = df['IMPACT'].value_counts().to_dict()
            summary['impact_distribution'] = impact_counts
        
        # Clinical significance
        if 'Clinical_Significance' in df.columns:
            clin_sig_counts = df['Clinical_Significance'].value_counts().to_dict()
            summary['clinical_significance_counts'] = clin_sig_counts
        
        # Top affected genes
        if 'Gene' in df.columns:
            top_genes = df['Gene'].value_counts().head(10).to_dict()
            summary['top_genes'] = top_genes
        
        # Save summary
        summary_file = outdir / "annotation_summary.json"
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Annotation summary saved to {summary_file}")
        return summary
        
    except Exception as e:
        logger.error(f"Failed to create annotation summary: {e}")
        return {}