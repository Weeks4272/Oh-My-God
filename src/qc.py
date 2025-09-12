"""
Quality control and trimming module using fastp.
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)


def run_qc(
    r1: str, 
    r2: Optional[str], 
    outdir: Path, 
    config: Dict[str, Any]
) -> Tuple[str, Optional[str]]:
    """
    Run quality control and trimming using fastp.
    
    Args:
        r1: Forward reads file path
        r2: Reverse reads file path (optional)
        outdir: Output directory
        config: Configuration dictionary
        
    Returns:
        Tuple of (trimmed_r1, trimmed_r2) file paths
    """
    logger.info("Starting quality control with fastp")
    
    qc_dir = outdir / "qc"
    qc_dir.mkdir(exist_ok=True)
    
    # Output file paths
    trimmed_r1 = qc_dir / "trimmed_R1.fastq.gz"
    trimmed_r2 = qc_dir / "trimmed_R2.fastq.gz" if r2 else None
    
    # fastp command
    cmd = [
        "fastp",
        "-i", r1,
        "-o", str(trimmed_r1),
        "--html", str(qc_dir / "fastp_report.html"),
        "--json", str(qc_dir / "fastp_report.json"),
        "--thread", str(config.get("threads", 4)),
        "--qualified_quality_phred", str(config.get("qc", {}).get("min_quality", 20)),
        "--length_required", str(config.get("qc", {}).get("min_length", 50)),
        "--detect_adapter_for_pe" if r2 else "--disable_adapter_trimming"
    ]
    
    if r2:
        cmd.extend(["-I", r2, "-O", str(trimmed_r2)])
    
    # Add additional fastp parameters from config
    fastp_params = config.get("qc", {}).get("fastp_params", [])
    cmd.extend(fastp_params)
    
    logger.info(f"Running fastp command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("fastp completed successfully")
        logger.debug(f"fastp stdout: {result.stdout}")
        
        # Log QC statistics
        _log_qc_stats(qc_dir / "fastp_report.json")
        
        return str(trimmed_r1), str(trimmed_r2) if trimmed_r2 else None
        
    except subprocess.CalledProcessError as e:
        logger.error(f"fastp failed with return code {e.returncode}")
        logger.error(f"fastp stderr: {e.stderr}")
        raise RuntimeError(f"Quality control failed: {e.stderr}")
    except FileNotFoundError:
        logger.error("fastp not found. Please install fastp.")
        raise RuntimeError("fastp not installed")


def _log_qc_stats(json_file: Path) -> None:
    """Log QC statistics from fastp JSON report."""
    try:
        import json
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        summary = data.get("summary", {})
        before = summary.get("before_filtering", {})
        after = summary.get("after_filtering", {})
        
        logger.info("QC Statistics:")
        logger.info(f"  Reads before filtering: {before.get('total_reads', 'N/A')}")
        logger.info(f"  Reads after filtering: {after.get('total_reads', 'N/A')}")
        logger.info(f"  Bases before filtering: {before.get('total_bases', 'N/A')}")
        logger.info(f"  Bases after filtering: {after.get('total_bases', 'N/A')}")
        
        if before.get('total_reads') and after.get('total_reads'):
            retention_rate = (after['total_reads'] / before['total_reads']) * 100
            logger.info(f"  Read retention rate: {retention_rate:.2f}%")
            
    except Exception as e:
        logger.warning(f"Could not parse QC statistics: {e}")


def validate_fastq_files(r1: str, r2: Optional[str] = None) -> bool:
    """
    Validate FASTQ file format and existence.
    
    Args:
        r1: Forward reads file path
        r2: Reverse reads file path (optional)
        
    Returns:
        True if files are valid, False otherwise
    """
    files_to_check = [r1]
    if r2:
        files_to_check.append(r2)
    
    for file_path in files_to_check:
        if not Path(file_path).exists():
            logger.error(f"FASTQ file not found: {file_path}")
            return False
        
        # Basic FASTQ format check
        try:
            with open(file_path, 'rt') as f:
                first_line = f.readline().strip()
                if not first_line.startswith('@'):
                    logger.error(f"Invalid FASTQ format in {file_path}: first line should start with '@'")
                    return False
        except Exception as e:
            logger.error(f"Could not read FASTQ file {file_path}: {e}")
            return False
    
    logger.info("FASTQ file validation passed")
    return True