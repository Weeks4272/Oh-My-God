"""
Read alignment module supporting both Illumina (bwa-mem2) and Nanopore (minimap2) platforms.
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def run_alignment(
    reads: tuple, 
    outdir: Path, 
    reference: Optional[str], 
    platform: str, 
    config: Dict[str, Any]
) -> str:
    """
    Align reads to reference genome.
    
    Args:
        reads: Tuple of (R1, R2) trimmed read files
        outdir: Output directory
        reference: Reference genome path (optional, uses config if None)
        platform: Sequencing platform ('illumina' or 'nanopore')
        config: Configuration dictionary
        
    Returns:
        Path to sorted BAM file
    """
    logger.info(f"Starting alignment for {platform} platform")
    
    align_dir = outdir / "alignment"
    align_dir.mkdir(exist_ok=True)
    
    # Get reference genome path
    if not reference:
        reference = config.get("reference", {}).get("genome")
        if not reference:
            raise ValueError("Reference genome path not provided")
    
    # Check if reference exists
    if not Path(reference).exists():
        raise FileNotFoundError(f"Reference genome not found: {reference}")
    
    # Output BAM file
    output_bam = align_dir / "aligned_sorted.bam"
    
    if platform.lower() == "illumina":
        return _align_illumina(reads, reference, output_bam, config)
    elif platform.lower() == "nanopore":
        return _align_nanopore(reads, reference, output_bam, config)
    else:
        raise ValueError(f"Unsupported platform: {platform}")


def _align_illumina(reads: tuple, reference: str, output_bam: Path, config: Dict[str, Any]) -> str:
    """Align Illumina reads using bwa-mem2."""
    r1, r2 = reads
    threads = config.get("threads", 4)
    
    logger.info("Aligning Illumina reads with bwa-mem2")
    
    # Check if bwa-mem2 index exists
    _ensure_bwa_index(reference)
    
    # Build bwa-mem2 command
    bwa_cmd = [
        "bwa-mem2", "mem",
        "-t", str(threads),
        "-M",  # Mark shorter split hits as secondary
        "-R", f"@RG\\tID:sample\\tSM:sample\\tPL:ILLUMINA\\tLB:lib1",
        reference,
        r1
    ]
    
    if r2:
        bwa_cmd.append(r2)
    
    # Add additional bwa-mem2 parameters
    bwa_params = config.get("alignment", {}).get("bwa_params", [])
    bwa_cmd.extend(bwa_params)
    
    # Samtools sort command
    sort_cmd = [
        "samtools", "sort",
        "-@", str(threads),
        "-o", str(output_bam),
        "-"
    ]
    
    logger.info(f"Running bwa-mem2 | samtools sort pipeline")
    
    try:
        # Run bwa-mem2 piped to samtools sort
        bwa_process = subprocess.Popen(bwa_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sort_process = subprocess.Popen(sort_cmd, stdin=bwa_process.stdout, stderr=subprocess.PIPE)
        
        bwa_process.stdout.close()
        sort_stdout, sort_stderr = sort_process.communicate()
        
        if sort_process.returncode != 0:
            raise subprocess.CalledProcessError(sort_process.returncode, sort_cmd, sort_stderr)
        
        # Index the BAM file
        _index_bam(output_bam, threads)
        
        logger.info("Illumina alignment completed successfully")
        return str(output_bam)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Alignment failed: {e}")
        raise RuntimeError(f"Illumina alignment failed: {e}")


def _align_nanopore(reads: tuple, reference: str, output_bam: Path, config: Dict[str, Any]) -> str:
    """Align Nanopore reads using minimap2."""
    r1, r2 = reads
    threads = config.get("threads", 4)
    
    logger.info("Aligning Nanopore reads with minimap2")
    
    # For Nanopore, typically only R1 is used
    input_reads = r1
    
    # minimap2 command
    minimap_cmd = [
        "minimap2",
        "-ax", "map-ont",  # Oxford Nanopore preset
        "-t", str(threads),
        "--secondary=no",  # Don't output secondary alignments
        reference,
        input_reads
    ]
    
    # Add additional minimap2 parameters
    minimap_params = config.get("alignment", {}).get("minimap2_params", [])
    minimap_cmd.extend(minimap_params)
    
    # Samtools sort command
    sort_cmd = [
        "samtools", "sort",
        "-@", str(threads),
        "-o", str(output_bam),
        "-"
    ]
    
    logger.info(f"Running minimap2 | samtools sort pipeline")
    
    try:
        # Run minimap2 piped to samtools sort
        minimap_process = subprocess.Popen(minimap_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sort_process = subprocess.Popen(sort_cmd, stdin=minimap_process.stdout, stderr=subprocess.PIPE)
        
        minimap_process.stdout.close()
        sort_stdout, sort_stderr = sort_process.communicate()
        
        if sort_process.returncode != 0:
            raise subprocess.CalledProcessError(sort_process.returncode, sort_cmd, sort_stderr)
        
        # Index the BAM file
        _index_bam(output_bam, threads)
        
        logger.info("Nanopore alignment completed successfully")
        return str(output_bam)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Alignment failed: {e}")
        raise RuntimeError(f"Nanopore alignment failed: {e}")


def _ensure_bwa_index(reference: str) -> None:
    """Ensure bwa-mem2 index exists for reference genome."""
    index_files = [f"{reference}.{ext}" for ext in ["0123", "ann", "amb", "pac", "bwt.2bit.64"]]
    
    if not all(Path(f).exists() for f in index_files):
        logger.info("Building bwa-mem2 index")
        cmd = ["bwa-mem2", "index", reference]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info("bwa-mem2 index created successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create bwa-mem2 index: {e.stderr}")
            raise RuntimeError(f"Index creation failed: {e.stderr}")


def _index_bam(bam_file: Path, threads: int) -> None:
    """Create BAM index file."""
    logger.info("Creating BAM index")
    
    cmd = ["samtools", "index", "-@", str(threads), str(bam_file)]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info("BAM index created successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create BAM index: {e.stderr}")
        raise RuntimeError(f"BAM indexing failed: {e.stderr}")


def get_alignment_stats(bam_file: str) -> Dict[str, Any]:
    """Get alignment statistics using samtools flagstat."""
    logger.info("Generating alignment statistics")
    
    cmd = ["samtools", "flagstat", bam_file]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Parse flagstat output
        lines = result.stdout.strip().split('\n')
        stats = {}
        
        for line in lines:
            if "mapped (" in line:
                parts = line.split()
                mapped_reads = int(parts[0])
                percentage = parts[4].strip('(%)').replace('%', '')
                stats['mapped_reads'] = mapped_reads
                stats['mapping_rate'] = float(percentage)
            elif "properly paired (" in line:
                parts = line.split()
                properly_paired = int(parts[0])
                percentage = parts[4].strip('(%)').replace('%', '')
                stats['properly_paired'] = properly_paired
                stats['proper_pair_rate'] = float(percentage)
        
        logger.info(f"Alignment statistics: {stats}")
        return stats
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get alignment statistics: {e.stderr}")
        return {}