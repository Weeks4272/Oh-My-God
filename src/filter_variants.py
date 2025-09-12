"""
Variant filtering module with depth and quality filters.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def filter_variants(
    vcf_file: str, 
    outdir: Path, 
    config: Dict[str, Any]
) -> str:
    """
    Filter variants based on depth and quality criteria.
    
    Args:
        vcf_file: Path to input VCF file
        outdir: Output directory
        config: Configuration dictionary
        
    Returns:
        Path to filtered VCF file
    """
    logger.info("Starting variant filtering")
    
    variants_dir = outdir / "variants"
    variants_dir.mkdir(exist_ok=True)
    
    filtered_vcf = variants_dir / "variants.filtered.vcf.gz"
    
    # Get filter parameters from config
    filter_config = config.get("variant_filtering", {})
    min_depth = filter_config.get("min_depth", 10)
    min_gq = filter_config.get("min_gq", 20)
    min_qual = filter_config.get("min_qual", 30)
    max_missing = filter_config.get("max_missing", 0.1)
    
    # Build bcftools filter expression
    filter_expressions = []
    
    # Quality filter
    filter_expressions.append(f"QUAL >= {min_qual}")
    
    # Depth filter (DP field)
    filter_expressions.append(f"INFO/DP >= {min_depth}")
    
    # Genotype quality filter (GQ field)
    filter_expressions.append(f"FORMAT/GQ >= {min_gq}")
    
    # Additional custom filters
    custom_filters = filter_config.get("custom_filters", [])
    filter_expressions.extend(custom_filters)
    
    # Combine all filters with AND
    filter_expression = " && ".join(filter_expressions)
    
    # bcftools filter command
    cmd = [
        "bcftools", "filter",
        "-i", filter_expression,
        "-O", "z",  # Output compressed VCF
        "-o", str(filtered_vcf),
        vcf_file
    ]
    
    logger.info(f"Running bcftools filter: {' '.join(cmd)}")
    logger.info(f"Filter expression: {filter_expression}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("bcftools filter completed successfully")
        
        # Index the filtered VCF
        _index_vcf(filtered_vcf)
        
        # Log filtering statistics
        _log_filtering_stats(vcf_file, str(filtered_vcf))
        
        # Apply additional quality filters if specified
        if filter_config.get("apply_hard_filters", False):
            filtered_vcf = _apply_hard_filters(str(filtered_vcf), variants_dir, filter_config)
        
        return str(filtered_vcf)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Variant filtering failed: {e.stderr}")
        raise RuntimeError(f"Variant filtering failed: {e.stderr}")


def _index_vcf(vcf_file: Path) -> None:
    """Create tabix index for VCF file."""
    logger.info("Creating VCF index")
    
    cmd = ["tabix", "-p", "vcf", str(vcf_file)]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info("VCF index created successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"VCF indexing failed: {e.stderr}")
        raise RuntimeError(f"VCF indexing failed: {e.stderr}")


def _log_filtering_stats(input_vcf: str, filtered_vcf: str) -> None:
    """Log variant filtering statistics."""
    try:
        # Count variants before filtering
        cmd_before = ["bcftools", "view", "-H", input_vcf, "|", "wc", "-l"]
        result_before = subprocess.run(
            " ".join(cmd_before), 
            shell=True, 
            capture_output=True, 
            text=True
        )
        variants_before = int(result_before.stdout.strip()) if result_before.stdout.strip() else 0
        
        # Count variants after filtering
        cmd_after = ["bcftools", "view", "-H", filtered_vcf, "|", "wc", "-l"]
        result_after = subprocess.run(
            " ".join(cmd_after), 
            shell=True, 
            capture_output=True, 
            text=True
        )
        variants_after = int(result_after.stdout.strip()) if result_after.stdout.strip() else 0
        
        # Calculate retention rate
        if variants_before > 0:
            retention_rate = (variants_after / variants_before) * 100
            logger.info(f"Filtering statistics:")
            logger.info(f"  Variants before filtering: {variants_before}")
            logger.info(f"  Variants after filtering: {variants_after}")
            logger.info(f"  Retention rate: {retention_rate:.2f}%")
        else:
            logger.warning("No variants found in input file")
            
    except Exception as e:
        logger.warning(f"Could not calculate filtering statistics: {e}")


def _apply_hard_filters(
    vcf_file: str, 
    outdir: Path, 
    filter_config: Dict[str, Any]
) -> str:
    """Apply hard filters for additional quality control."""
    logger.info("Applying hard filters")
    
    hard_filtered_vcf = outdir / "variants.hard_filtered.vcf.gz"
    
    # Hard filter parameters
    hard_filters = filter_config.get("hard_filters", {})
    
    # Build GATK VariantFiltration command if available
    cmd = [
        "gatk", "VariantFiltration",
        "-V", vcf_file,
        "-O", str(hard_filtered_vcf)
    ]
    
    # Add filter expressions
    for filter_name, filter_expr in hard_filters.items():
        cmd.extend(["--filter-expression", filter_expr, "--filter-name", filter_name])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Hard filters applied successfully")
        
        # Remove filtered variants (keep only PASS)
        pass_only_vcf = outdir / "variants.pass_only.vcf.gz"
        pass_cmd = [
            "bcftools", "view",
            "-f", "PASS",
            "-O", "z",
            "-o", str(pass_only_vcf),
            str(hard_filtered_vcf)
        ]
        
        subprocess.run(pass_cmd, check=True)
        _index_vcf(pass_only_vcf)
        
        return str(pass_only_vcf)
        
    except subprocess.CalledProcessError as e:
        logger.warning(f"Hard filtering failed, using soft filters only: {e}")
        return vcf_file
    except FileNotFoundError:
        logger.warning("GATK not available for hard filtering, using soft filters only")
        return vcf_file


def filter_by_region(
    vcf_file: str, 
    regions: list, 
    outdir: Path
) -> str:
    """
    Filter variants by genomic regions.
    
    Args:
        vcf_file: Input VCF file
        regions: List of regions in format "chr:start-end"
        outdir: Output directory
        
    Returns:
        Path to region-filtered VCF file
    """
    logger.info(f"Filtering variants by {len(regions)} regions")
    
    region_filtered_vcf = outdir / "variants.region_filtered.vcf.gz"
    
    # Create regions file
    regions_file = outdir / "filter_regions.bed"
    with open(regions_file, 'w') as f:
        for region in regions:
            # Convert "chr:start-end" to BED format
            if ':' in region and '-' in region:
                chrom, pos_range = region.split(':')
                start, end = pos_range.split('-')
                f.write(f"{chrom}\t{start}\t{end}\n")
    
    # bcftools view with regions
    cmd = [
        "bcftools", "view",
        "-R", str(regions_file),
        "-O", "z",
        "-o", str(region_filtered_vcf),
        vcf_file
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        _index_vcf(region_filtered_vcf)
        
        logger.info("Region filtering completed successfully")
        return str(region_filtered_vcf)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Region filtering failed: {e.stderr}")
        raise RuntimeError(f"Region filtering failed: {e.stderr}")


def annotate_filter_flags(vcf_file: str, outdir: Path) -> str:
    """
    Annotate variants with filter flags without removing them.
    
    Args:
        vcf_file: Input VCF file
        outdir: Output directory
        
    Returns:
        Path to annotated VCF file
    """
    logger.info("Annotating variants with filter flags")
    
    annotated_vcf = outdir / "variants.annotated_filters.vcf.gz"
    
    # This would use GATK VariantFiltration to add filter annotations
    # without actually filtering out variants
    cmd = [
        "bcftools", "annotate",
        "-O", "z",
        "-o", str(annotated_vcf),
        vcf_file
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        _index_vcf(annotated_vcf)
        
        logger.info("Filter annotation completed successfully")
        return str(annotated_vcf)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Filter annotation failed: {e.stderr}")
        return vcf_file  # Return original file if annotation fails