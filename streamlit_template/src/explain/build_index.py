"""
Build FAISS index from ClinVar summaries for similarity search.
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

try:
    import faiss
except ImportError:
    logger.error("FAISS not installed. Please install with: pip install faiss-cpu")
    faiss = None


def build_clinvar_index(config: Dict[str, Any]) -> str:
    """
    Build FAISS index from ClinVar data for similarity search.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Path to saved index
    """
    if faiss is None:
        raise ImportError("FAISS not available")
    
    logger.info("Building ClinVar FAISS index")
    
    explain_config = config.get("explain", {})
    
    # Load ClinVar data
    clinvar_data = _load_clinvar_data(explain_config)
    
    # Generate embeddings
    embeddings, metadata = _generate_embeddings(clinvar_data, explain_config)
    
    # Build FAISS index
    index_path = _build_faiss_index(embeddings, metadata, explain_config)
    
    logger.info(f"FAISS index built successfully: {index_path}")
    return index_path


def _load_clinvar_data(config: Dict[str, Any]) -> pd.DataFrame:
    """Load ClinVar data from file or create mock data."""
    
    clinvar_file = config.get("clinvar_file")
    
    if clinvar_file and Path(clinvar_file).exists():
        logger.info(f"Loading ClinVar data from {clinvar_file}")
        
        # Determine file format and load accordingly
        if clinvar_file.endswith('.tsv') or clinvar_file.endswith('.txt'):
            df = pd.read_csv(clinvar_file, sep='\t', low_memory=False)
        elif clinvar_file.endswith('.csv'):
            df = pd.read_csv(clinvar_file, low_memory=False)
        elif clinvar_file.endswith('.parquet'):
            df = pd.read_parquet(clinvar_file)
        else:
            raise ValueError(f"Unsupported file format: {clinvar_file}")
        
        logger.info(f"Loaded {len(df)} ClinVar records")
        return df
    
    else:
        logger.warning("ClinVar file not found, creating mock data for demonstration")
        return _create_mock_clinvar_data()


def _create_mock_clinvar_data() -> pd.DataFrame:
    """Create mock ClinVar data for demonstration purposes."""
    
    mock_data = [
        {
            'VariationID': 'VCV000001',
            'Gene': 'BRCA1',
            'Consequence': 'missense_variant',
            'ClinicalSignificance': 'Pathogenic',
            'ReviewStatus': 'criteria provided, multiple submitters, no conflicts',
            'Condition': 'Hereditary breast and ovarian cancer syndrome',
            'Summary': 'This variant in BRCA1 is associated with increased risk of breast and ovarian cancer. Multiple studies have demonstrated pathogenicity.',
            'ChromosomeAccession': 'NC_000017.11',
            'Start': 43104121,
            'ReferenceAllele': 'A',
            'AlternateAllele': 'T'
        },
        {
            'VariationID': 'VCV000002',
            'Gene': 'TP53',
            'Consequence': 'stop_gained',
            'ClinicalSignificance': 'Pathogenic',
            'ReviewStatus': 'reviewed by expert panel',
            'Condition': 'Li-Fraumeni syndrome',
            'Summary': 'This nonsense variant in TP53 results in a premature stop codon and is associated with Li-Fraumeni syndrome.',
            'ChromosomeAccession': 'NC_000017.11',
            'Start': 7674220,
            'ReferenceAllele': 'C',
            'AlternateAllele': 'T'
        },
        {
            'VariationID': 'VCV000003',
            'Gene': 'CFTR',
            'Consequence': 'frameshift_variant',
            'ClinicalSignificance': 'Pathogenic',
            'ReviewStatus': 'criteria provided, multiple submitters, no conflicts',
            'Condition': 'Cystic fibrosis',
            'Summary': 'This frameshift variant in CFTR is a common cause of cystic fibrosis in European populations.',
            'ChromosomeAccession': 'NC_000007.14',
            'Start': 117559590,
            'ReferenceAllele': 'CTT',
            'AlternateAllele': 'C'
        },
        {
            'VariationID': 'VCV000004',
            'Gene': 'APOE',
            'Consequence': 'missense_variant',
            'ClinicalSignificance': 'risk factor',
            'ReviewStatus': 'reviewed by expert panel',
            'Condition': 'Alzheimer disease',
            'Summary': 'The APOE e4 allele is a major genetic risk factor for late-onset Alzheimer disease.',
            'ChromosomeAccession': 'NC_000019.10',
            'Start': 44908684,
            'ReferenceAllele': 'T',
            'AlternateAllele': 'C'
        },
        {
            'VariationID': 'VCV000005',
            'Gene': 'HBB',
            'Consequence': 'missense_variant',
            'ClinicalSignificance': 'Pathogenic',
            'ReviewStatus': 'criteria provided, multiple submitters, no conflicts',
            'Condition': 'Sickle cell anemia',
            'Summary': 'This variant causes sickle cell anemia by altering hemoglobin structure and function.',
            'ChromosomeAccession': 'NC_000011.10',
            'Start': 5227002,
            'ReferenceAllele': 'T',
            'AlternateAllele': 'A'
        }
    ]
    
    # Expand with more variants for better demonstration
    expanded_data = []
    for i, base_variant in enumerate(mock_data):
        for j in range(20):  # Create 20 variants per base
            variant = base_variant.copy()
            variant['VariationID'] = f"VCV{i:06d}_{j:03d}"
            variant['Start'] = variant['Start'] + j * 100
            
            # Vary clinical significance
            if j % 4 == 0:
                variant['ClinicalSignificance'] = 'Benign'
                variant['Summary'] = f"This variant in {variant['Gene']} is considered benign based on population frequency and functional studies."
            elif j % 4 == 1:
                variant['ClinicalSignificance'] = 'Likely benign'
                variant['Summary'] = f"This variant in {variant['Gene']} is likely benign but requires further study."
            elif j % 4 == 2:
                variant['ClinicalSignificance'] = 'Uncertain significance'
                variant['Summary'] = f"The clinical significance of this {variant['Gene']} variant is currently uncertain."
            
            expanded_data.append(variant)
    
    df = pd.DataFrame(expanded_data)
    logger.info(f"Created {len(df)} mock ClinVar records")
    return df


def _generate_embeddings(df: pd.DataFrame, config: Dict[str, Any]) -> tuple:
    """Generate sentence embeddings for ClinVar summaries."""
    
    logger.info("Generating embeddings for ClinVar summaries")
    
    # Load sentence transformer model
    model_name = config.get("embedding_model", "all-MiniLM-L6-v2")
    model = SentenceTransformer(model_name)
    
    # Prepare text for embedding
    texts = []
    metadata = []
    
    for idx, row in df.iterrows():
        # Combine multiple fields for richer context
        text_parts = []
        
        if pd.notna(row.get('Gene')):
            text_parts.append(f"Gene: {row['Gene']}")
        
        if pd.notna(row.get('Consequence')):
            text_parts.append(f"Consequence: {row['Consequence']}")
        
        if pd.notna(row.get('ClinicalSignificance')):
            text_parts.append(f"Clinical significance: {row['ClinicalSignificance']}")
        
        if pd.notna(row.get('Condition')):
            text_parts.append(f"Condition: {row['Condition']}")
        
        if pd.notna(row.get('Summary')):
            text_parts.append(f"Summary: {row['Summary']}")
        
        combined_text = " | ".join(text_parts)
        texts.append(combined_text)
        
        # Store metadata for retrieval
        metadata.append({
            'variation_id': row.get('VariationID', ''),
            'gene': row.get('Gene', ''),
            'consequence': row.get('Consequence', ''),
            'clinical_significance': row.get('ClinicalSignificance', ''),
            'condition': row.get('Condition', ''),
            'summary': row.get('Summary', ''),
            'review_status': row.get('ReviewStatus', ''),
            'chromosome': row.get('ChromosomeAccession', ''),
            'position': row.get('Start', 0),
            'ref_allele': row.get('ReferenceAllele', ''),
            'alt_allele': row.get('AlternateAllele', '')
        })
    
    # Generate embeddings
    logger.info(f"Generating embeddings for {len(texts)} entries")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    logger.info(f"Generated embeddings with shape: {embeddings.shape}")
    return embeddings, metadata


def _build_faiss_index(embeddings: np.ndarray, metadata: List[Dict], config: Dict[str, Any]) -> str:
    """Build and save FAISS index."""
    
    logger.info("Building FAISS index")
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    
    # Add embeddings to index
    index.add(embeddings.astype(np.float32))
    
    logger.info(f"Added {index.ntotal} vectors to FAISS index")
    
    # Save index and metadata
    index_dir = Path(config.get("index_dir", "faiss_index"))
    index_dir.mkdir(exist_ok=True)
    
    index_file = index_dir / "clinvar_index.faiss"
    metadata_file = index_dir / "clinvar_metadata.pkl"
    
    # Save FAISS index
    faiss.write_index(index, str(index_file))
    
    # Save metadata
    with open(metadata_file, 'wb') as f:
        pickle.dump(metadata, f)
    
    # Save configuration for loading
    config_file = index_dir / "index_config.pkl"
    index_config = {
        'embedding_model': config.get("embedding_model", "all-MiniLM-L6-v2"),
        'dimension': dimension,
        'num_vectors': len(embeddings),
        'created_at': pd.Timestamp.now().isoformat()
    }
    
    with open(config_file, 'wb') as f:
        pickle.dump(index_config, f)
    
    logger.info(f"FAISS index saved to {index_file}")
    logger.info(f"Metadata saved to {metadata_file}")
    
    return str(index_dir)


def update_index(new_data: pd.DataFrame, index_dir: str, config: Dict[str, Any]) -> None:
    """Update existing FAISS index with new data."""
    
    logger.info("Updating FAISS index with new data")
    
    # This would implement incremental index updates
    # For now, we rebuild the entire index
    logger.warning("Incremental updates not implemented, rebuilding entire index")
    
    # Load existing metadata
    metadata_file = Path(index_dir) / "clinvar_metadata.pkl"
    if metadata_file.exists():
        with open(metadata_file, 'rb') as f:
            existing_metadata = pickle.load(f)
        
        # Combine with new data and rebuild
        # Implementation would merge dataframes and rebuild
        pass
    
    # For now, just rebuild with new data
    build_clinvar_index(config)


def validate_index(index_dir: str) -> bool:
    """Validate FAISS index integrity."""
    
    logger.info(f"Validating FAISS index at {index_dir}")
    
    index_path = Path(index_dir)
    
    required_files = [
        "clinvar_index.faiss",
        "clinvar_metadata.pkl",
        "index_config.pkl"
    ]
    
    for file_name in required_files:
        file_path = index_path / file_name
        if not file_path.exists():
            logger.error(f"Missing required file: {file_path}")
            return False
    
    try:
        # Load and test index
        index_file = index_path / "clinvar_index.faiss"
        index = faiss.read_index(str(index_file))
        
        # Load metadata
        metadata_file = index_path / "clinvar_metadata.pkl"
        with open(metadata_file, 'rb') as f:
            metadata = pickle.load(f)
        
        # Check consistency
        if index.ntotal != len(metadata):
            logger.error(f"Index size mismatch: {index.ntotal} vs {len(metadata)}")
            return False
        
        logger.info(f"Index validation passed: {index.ntotal} vectors")
        return True
        
    except Exception as e:
        logger.error(f"Index validation failed: {e}")
        return False