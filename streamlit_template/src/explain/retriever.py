"""
Similarity search and retrieval module using FAISS index.
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

try:
    import faiss
except ImportError:
    logger.error("FAISS not installed. Please install with: pip install faiss-cpu")
    faiss = None


class VariantRetriever:
    """Retriever for finding similar variants using FAISS index."""
    
    def __init__(self, index_dir: str, config: Dict[str, Any]):
        """
        Initialize retriever with FAISS index.
        
        Args:
            index_dir: Directory containing FAISS index files
            config: Configuration dictionary
        """
        self.index_dir = Path(index_dir)
        self.config = config
        self.index = None
        self.metadata = None
        self.model = None
        
        self._load_index()
    
    def _load_index(self) -> None:
        """Load FAISS index and metadata."""
        if faiss is None:
            raise ImportError("FAISS not available")
        
        logger.info(f"Loading FAISS index from {self.index_dir}")
        
        # Load index
        index_file = self.index_dir / "clinvar_index.faiss"
        if not index_file.exists():
            raise FileNotFoundError(f"FAISS index not found: {index_file}")
        
        self.index = faiss.read_index(str(index_file))
        
        # Load metadata
        metadata_file = self.index_dir / "clinvar_metadata.pkl"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
        
        with open(metadata_file, 'rb') as f:
            self.metadata = pickle.load(f)
        
        # Load configuration
        config_file = self.index_dir / "index_config.pkl"
        if config_file.exists():
            with open(config_file, 'rb') as f:
                index_config = pickle.load(f)
                model_name = index_config.get('embedding_model', 'all-MiniLM-L6-v2')
        else:
            model_name = self.config.get("explain", {}).get("embedding_model", "all-MiniLM-L6-v2")
        
        # Load sentence transformer model
        self.model = SentenceTransformer(model_name)
        
        logger.info(f"Loaded index with {self.index.ntotal} vectors")
    
    def search_similar_variants(
        self, 
        query_variant: Dict[str, Any], 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar variants in the index.
        
        Args:
            query_variant: Variant information dictionary
            k: Number of similar variants to retrieve
            
        Returns:
            List of similar variants with similarity scores
        """
        logger.info(f"Searching for {k} similar variants")
        
        # Create query text from variant information
        query_text = self._create_query_text(query_variant)
        
        # Generate embedding for query
        query_embedding = self.model.encode([query_text])
        faiss.normalize_L2(query_embedding)
        
        # Search index
        similarities, indices = self.index.search(query_embedding.astype(np.float32), k)
        
        # Retrieve similar variants
        similar_variants = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(self.metadata):
                variant_info = self.metadata[idx].copy()
                variant_info['similarity_score'] = float(similarity)
                variant_info['rank'] = i + 1
                similar_variants.append(variant_info)
        
        logger.info(f"Found {len(similar_variants)} similar variants")
        return similar_variants
    
    def _create_query_text(self, variant: Dict[str, Any]) -> str:
        """Create query text from variant information."""
        
        text_parts = []
        
        # Add gene information
        if variant.get('Gene'):
            text_parts.append(f"Gene: {variant['Gene']}")
        
        # Add consequence type
        if variant.get('Consequence'):
            text_parts.append(f"Consequence: {variant['Consequence']}")
        
        # Add clinical significance if available
        if variant.get('Clinical_Significance'):
            text_parts.append(f"Clinical significance: {variant['Clinical_Significance']}")
        
        # Add impact level
        if variant.get('IMPACT'):
            text_parts.append(f"Impact: {variant['IMPACT']}")
        
        # Add protein change if available
        if variant.get('Protein_position') or variant.get('Amino_acids'):
            protein_info = []
            if variant.get('Protein_position'):
                protein_info.append(f"position {variant['Protein_position']}")
            if variant.get('Amino_acids'):
                protein_info.append(f"amino acid change {variant['Amino_acids']}")
            text_parts.append(f"Protein: {' '.join(protein_info)}")
        
        # Add any existing variation ID
        if variant.get('Existing_variation'):
            text_parts.append(f"Known variant: {variant['Existing_variation']}")
        
        query_text = " | ".join(text_parts)
        logger.debug(f"Query text: {query_text}")
        
        return query_text
    
    def batch_search(
        self, 
        variants: List[Dict[str, Any]], 
        k: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for similar variants for multiple query variants.
        
        Args:
            variants: List of variant dictionaries
            k: Number of similar variants to retrieve per query
            
        Returns:
            Dictionary mapping variant IDs to similar variants
        """
        logger.info(f"Batch searching for {len(variants)} variants")
        
        results = {}
        
        for variant in variants:
            variant_id = variant.get('Variant_ID', f"variant_{len(results)}")
            
            try:
                similar_variants = self.search_similar_variants(variant, k)
                results[variant_id] = similar_variants
            except Exception as e:
                logger.error(f"Failed to search for variant {variant_id}: {e}")
                results[variant_id] = []
        
        logger.info(f"Completed batch search for {len(results)} variants")
        return results


def retrieve_similar_variants(
    variants_file: str, 
    config: Dict[str, Any]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve similar variants for all variants in a file.
    
    Args:
        variants_file: Path to annotated variants parquet file
        config: Configuration dictionary
        
    Returns:
        Dictionary of similar variants for each query variant
    """
    logger.info(f"Retrieving similar variants for file: {variants_file}")
    
    # Load variants
    if variants_file.endswith('.parquet'):
        df = pd.read_parquet(variants_file)
    elif variants_file.endswith('.tsv'):
        df = pd.read_csv(variants_file, sep='\t')
    else:
        raise ValueError(f"Unsupported file format: {variants_file}")
    
    if df.empty:
        logger.warning("No variants found in input file")
        return {}
    
    # Initialize retriever
    explain_config = config.get("explain", {})
    index_dir = explain_config.get("index_dir", "faiss_index")
    
    if not Path(index_dir).exists():
        logger.error(f"FAISS index directory not found: {index_dir}")
        raise FileNotFoundError(f"FAISS index not found. Please build index first.")
    
    retriever = VariantRetriever(index_dir, config)
    
    # Convert dataframe to list of dictionaries
    variants = df.to_dict('records')
    
    # Limit number of variants for efficiency
    max_variants = explain_config.get("max_variants_to_explain", 100)
    if len(variants) > max_variants:
        logger.info(f"Limiting to top {max_variants} variants by priority score")
        
        # Sort by priority score if available
        if 'Priority_Rank' in df.columns:
            df_sorted = df.sort_values('Priority_Rank')
        elif 'Pathogenicity_Score' in df.columns:
            df_sorted = df.sort_values('Pathogenicity_Score', ascending=False)
        else:
            df_sorted = df.head(max_variants)
        
        variants = df_sorted.head(max_variants).to_dict('records')
    
    # Retrieve similar variants
    k = explain_config.get("num_similar_variants", 5)
    similar_variants = retriever.batch_search(variants, k)
    
    return similar_variants


def create_retrieval_summary(
    similar_variants: Dict[str, List[Dict[str, Any]]], 
    outdir: Path
) -> Dict[str, Any]:
    """Create summary of retrieval results."""
    
    logger.info("Creating retrieval summary")
    
    summary = {
        'total_query_variants': len(similar_variants),
        'total_retrieved_variants': sum(len(variants) for variants in similar_variants.values()),
        'average_similarity_scores': {},
        'top_genes_retrieved': {},
        'clinical_significance_distribution': {}
    }
    
    # Collect all retrieved variants for analysis
    all_retrieved = []
    for variants in similar_variants.values():
        all_retrieved.extend(variants)
    
    if all_retrieved:
        # Calculate average similarity scores
        similarity_scores = [v.get('similarity_score', 0) for v in all_retrieved]
        summary['average_similarity_scores'] = {
            'mean': np.mean(similarity_scores),
            'median': np.median(similarity_scores),
            'std': np.std(similarity_scores)
        }
        
        # Top genes
        genes = [v.get('gene', 'Unknown') for v in all_retrieved if v.get('gene')]
        gene_counts = pd.Series(genes).value_counts().head(10).to_dict()
        summary['top_genes_retrieved'] = gene_counts
        
        # Clinical significance distribution
        clin_sig = [v.get('clinical_significance', 'Unknown') for v in all_retrieved]
        clin_sig_counts = pd.Series(clin_sig).value_counts().to_dict()
        summary['clinical_significance_distribution'] = clin_sig_counts
    
    # Save summary
    summary_file = outdir / "retrieval_summary.json"
    import json
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    logger.info(f"Retrieval summary saved to {summary_file}")
    return summary


def filter_retrieved_variants(
    similar_variants: Dict[str, List[Dict[str, Any]]], 
    config: Dict[str, Any]
) -> Dict[str, List[Dict[str, Any]]]:
    """Filter retrieved variants based on quality criteria."""
    
    logger.info("Filtering retrieved variants")
    
    explain_config = config.get("explain", {})
    min_similarity = explain_config.get("min_similarity_threshold", 0.5)
    required_fields = explain_config.get("required_fields", ["gene", "clinical_significance"])
    
    filtered_variants = {}
    
    for variant_id, variants in similar_variants.items():
        filtered = []
        
        for variant in variants:
            # Check similarity threshold
            if variant.get('similarity_score', 0) < min_similarity:
                continue
            
            # Check required fields
            if not all(variant.get(field) for field in required_fields):
                continue
            
            # Filter out uncertain or conflicting entries for high-confidence explanations
            clin_sig = variant.get('clinical_significance', '').lower()
            if 'uncertain' in clin_sig or 'conflicting' in clin_sig:
                if explain_config.get("exclude_uncertain", False):
                    continue
            
            filtered.append(variant)
        
        filtered_variants[variant_id] = filtered
    
    total_before = sum(len(v) for v in similar_variants.values())
    total_after = sum(len(v) for v in filtered_variants.values())
    
    logger.info(f"Filtered variants: {total_before} -> {total_after}")
    return filtered_variants