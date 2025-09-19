"""
Variant calling module using FreeBayes.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def call_variants(
    bam_file: str, 
    outdir: Path, 
    reference: str, 
    config: Dict[str, Any]
) -> str:
    """
    Call variants using FreeBayes.
    
    Args:
        bam_file: Path to sorted BAM file
        outdir: Output directory
        reference: Reference genome path
        config: Configuration dictionary
        
    Returns:
        Path to VCF file
    """
    logger.info("Starting variant calling with FreeBayes")
    
    variants_dir = outdir / "variants"
    variants_dir.mkdir(exist_ok=True)
    
    output_vcf = variants_dir / "variants.vcf"
    
    # FreeBayes command
    cmd = [
        "freebayes",
        "-f", reference,
        "-v", str(output_vcf),
        bam_file
    ]
    
    # Add FreeBayes parameters from config
    freebayes_config = config.get("variant_calling", {})
    
    # Minimum base quality
    min_base_quality = freebayes_config.get("min_base_quality", 20)
    cmd.extend(["-q", str(min_base_quality)])
    
    # Minimum mapping quality
    min_mapping_quality = freebayes_config.get("min_mapping_quality", 20)
    cmd.extend(["-m", str(min_mapping_quality)])
    
    # Minimum alternate fraction
    min_alt_fraction = freebayes_config.get("min_alt_fraction", 0.2)
    cmd.extend(["-F", str(min_alt_fraction)])
    
    # Minimum coverage
    min_coverage = freebayes_config.get("min_coverage", 4)
    cmd.extend(["-C", str(min_coverage)])
    
    # Additional parameters
    additional_params = freebayes_config.get("additional_params", [])
    cmd.extend(additional_params)
    
    logger.info(f"Running FreeBayes command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("FreeBayes completed successfully")
        
        # Compress and index VCF
        compressed_vcf = _compress_and_index_vcf(output_vcf)
        
        # Log variant statistics
        _log_variant_stats(compressed_vcf)
        
        return compressed_vcf
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FreeBayes failed with return code {e.returncode}")
        logger.error(f"FreeBayes stderr: {e.stderr}")
        raise RuntimeError(f"Variant calling failed: {e.stderr}")
    except FileNotFoundError:
        logger.error("FreeBayes not found. Please install FreeBayes.")
        raise RuntimeError("FreeBayes not installed")


def _compress_and_index_vcf(vcf_file: Path) -> str:
    """Compress VCF file with bgzip and create tabix index."""
    logger.info("Compressing and indexing VCF file")
    
    compressed_vcf = f"{vcf_file}.gz"
    
    # Compress with bgzip
    bgzip_cmd = ["bgzip", "-c", str(vcf_file)]
    
    try:
        with open(compressed_vcf, 'wb') as f:
            subprocess.run(bgzip_cmd, check=True, stdout=f)
        
        # Create tabix index
        tabix_cmd = ["tabix", "-p", "vcf", compressed_vcf]
        subprocess.run(tabix_cmd, check=True)
        
        logger.info("VCF compression and indexing completed")
        return compressed_vcf
        
    except subprocess.CalledProcessError as e:
        logger.error(f"VCF compression/indexing failed: {e}")
        raise RuntimeError(f"VCF processing failed: {e}")


def _log_variant_stats(vcf_file: str) -> None:
    """Log basic variant statistics."""
    try:
        # Count variants using bcftools
        cmd = ["bcftools", "stats", vcf_file]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        lines = result.stdout.split('\n')
        for line in lines:
            if line.startswith('SN'):
                parts = line.split('\t')
                if len(parts) >= 3:
                    metric = parts[2].strip(':')
                    value = parts[3] if len(parts) > 3 else ''
                    
                    if 'number of records' in metric:
                        logger.info(f"Total variants: {value}")
                    elif 'number of SNPs' in metric:
                        logger.info(f"SNPs: {value}")
                    elif 'number of indels' in metric:
                        logger.info(f"Indels: {value}")
                        
    except Exception as e:
        logger.warning(f"Could not generate variant statistics: {e}")


def call_variants_gatk(
    bam_file: str, 
    outdir: Path, 
    reference: str, 
    config: Dict[str, Any]
) -> str:
    """
    Alternative variant calling using GATK HaplotypeCaller.
    This is for future implementation when GATK is preferred over FreeBayes.
    
    Args:
        bam_file: Path to sorted BAM file
        outdir: Output directory
        reference: Reference genome path
        config: Configuration dictionary
        
    Returns:
        Path to VCF file
    """
    logger.info("Starting variant calling with GATK HaplotypeCaller")
    
    variants_dir = outdir / "variants"
    variants_dir.mkdir(exist_ok=True)
    
    output_vcf = variants_dir / "variants_gatk.vcf.gz"
    
    # GATK HaplotypeCaller command
    cmd = [
        "gatk", "HaplotypeCaller",
        "-R", reference,
        "-I", bam_file,
        "-O", str(output_vcf)
    ]
    
    # Add GATK parameters from config
    gatk_config = config.get("variant_calling", {}).get("gatk", {})
    
    # Standard confidence threshold
    stand_call_conf = gatk_config.get("stand_call_conf", 30)
    cmd.extend(["--standard-min-confidence-threshold-for-calling", str(stand_call_conf)])
    
    # Additional parameters
    additional_params = gatk_config.get("additional_params", [])
    cmd.extend(additional_params)
    
    logger.info(f"Running GATK HaplotypeCaller: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("GATK HaplotypeCaller completed successfully")
        
        # Log variant statistics
        _log_variant_stats(str(output_vcf))
        
        return str(output_vcf)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"GATK failed with return code {e.returncode}")
        logger.error(f"GATK stderr: {e.stderr}")
        raise RuntimeError(f"GATK variant calling failed: {e.stderr}")
    except FileNotFoundError:
        logger.error("GATK not found. Please install GATK.")
        raise RuntimeError("GATK not installed")


def validate_vcf(vcf_file: str) -> bool:
    """
    Validate VCF file format.
    
    Args:
        vcf_file: Path to VCF file
        
    Returns:
        True if VCF is valid, False otherwise
    """
    logger.info(f"Validating VCF file: {vcf_file}")
    
    try:
        # Use bcftools to validate VCF
        cmd = ["bcftools", "view", "-h", vcf_file]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check for required VCF headers
        headers = result.stdout
        if not headers.startswith('##fileformat=VCF'):
            logger.error("Invalid VCF format: missing fileformat header")
            return False
        
        if '#CHROM' not in headers:
            logger.error("Invalid VCF format: missing column headers")
            return False
        
        logger.info("VCF validation passed")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"VCF validation failed: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("bcftools not found for VCF validation")
        return False