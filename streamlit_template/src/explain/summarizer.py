"""
AI summarization module using local LLM for variant explanations.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd

from .retriever import retrieve_similar_variants, filter_retrieved_variants
from .templates import get_explanation_template, format_variant_context

logger = logging.getLogger(__name__)

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    logger.warning("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
    LLAMA_CPP_AVAILABLE = False


class VariantSummarizer:
    """Summarizer for generating AI explanations of genetic variants."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize summarizer with LLM configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.llm = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load local LLM model."""
        if not LLAMA_CPP_AVAILABLE:
            logger.error("llama-cpp-python not available for local LLM")
            return
        
        explain_config = self.config.get("explain", {})
        llm_config = explain_config.get("llm", {})
        
        model_path = llm_config.get("model_path")
        if not model_path or not Path(model_path).exists():
            logger.warning("LLM model not found, using mock explanations")
            return
        
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=llm_config.get("context_length", 2048),
                n_threads=llm_config.get("threads", 4),
                verbose=False
            )
            logger.info(f"Loaded LLM model: {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load LLM model: {e}")
            self.llm = None
    
    def generate_explanation(
        self, 
        variant: Dict[str, Any], 
        similar_variants: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate AI explanation for a variant.
        
        Args:
            variant: Query variant information
            similar_variants: List of similar variants from database
            
        Returns:
            Dictionary containing explanation and metadata
        """
        logger.debug(f"Generating explanation for variant: {variant.get('Variant_ID', 'Unknown')}")
        
        if self.llm is None:
            return self._generate_mock_explanation(variant, similar_variants)
        
        # Create prompt from template
        prompt = self._create_prompt(variant, similar_variants)
        
        # Generate explanation using LLM
        try:
            response = self.llm(
                prompt,
                max_tokens=self.config.get("explain", {}).get("llm", {}).get("max_tokens", 300),
                temperature=self.config.get("explain", {}).get("llm", {}).get("temperature", 0.7),
                stop=["Human:", "Assistant:", "\n\n"]
            )
            
            explanation_text = response['choices'][0]['text'].strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            explanation_text = self._generate_fallback_explanation(variant, similar_variants)
        
        # Create explanation object
        explanation = {
            'variant_id': variant.get('Variant_ID', ''),
            'gene': variant.get('Gene', ''),
            'consequence': variant.get('Consequence', ''),
            'explanation': explanation_text,
            'confidence_score': self._calculate_confidence(variant, similar_variants),
            'evidence_count': len(similar_variants),
            'similar_variants': [v.get('variation_id', '') for v in similar_variants[:3]],
            'clinical_significance': variant.get('Clinical_Significance', ''),
            'pathogenicity_score': variant.get('Pathogenicity_Score', 0),
            'databases_used': ['ClinVar', 'gnomAD', 'Ensembl VEP'],
            'disclaimers': [
                "This analysis is for research purposes only and should not be used for medical diagnosis.",
                "Consult with a qualified healthcare provider for clinical interpretation.",
                "Variant interpretation may change as new evidence becomes available."
            ]
        }
        
        return explanation
    
    def _create_prompt(self, variant: Dict[str, Any], similar_variants: List[Dict[str, Any]]) -> str:
        """Create prompt for LLM from variant and similar variants."""
        
        # Get prompt template
        template = get_explanation_template()
        
        # Format variant context
        variant_context = format_variant_context(variant)
        
        # Format similar variants context
        similar_context = self._format_similar_variants(similar_variants)
        
        # Fill template
        prompt = template.format(
            variant_context=variant_context,
            similar_variants_context=similar_context,
            gene=variant.get('Gene', 'Unknown'),
            consequence=variant.get('Consequence', 'Unknown')
        )
        
        return prompt
    
    def _format_similar_variants(self, similar_variants: List[Dict[str, Any]]) -> str:
        """Format similar variants for prompt context."""
        
        if not similar_variants:
            return "No similar variants found in database."
        
        context_parts = []
        for i, variant in enumerate(similar_variants[:3], 1):  # Limit to top 3
            part = f"{i}. {variant.get('gene', 'Unknown gene')} variant"
            
            if variant.get('clinical_significance'):
                part += f" - {variant['clinical_significance']}"
            
            if variant.get('condition'):
                part += f" (associated with {variant['condition']})"
            
            if variant.get('summary'):
                # Truncate long summaries
                summary = variant['summary'][:200] + "..." if len(variant['summary']) > 200 else variant['summary']
                part += f": {summary}"
            
            context_parts.append(part)
        
        return "\n".join(context_parts)
    
    def _calculate_confidence(self, variant: Dict[str, Any], similar_variants: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for explanation."""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on evidence
        if similar_variants:
            avg_similarity = sum(v.get('similarity_score', 0) for v in similar_variants) / len(similar_variants)
            confidence += avg_similarity * 0.3
        
        # Increase confidence for well-characterized consequences
        consequence = variant.get('Consequence', '')
        high_confidence_consequences = ['stop_gained', 'frameshift_variant', 'splice_acceptor_variant']
        if any(cons in consequence for cons in high_confidence_consequences):
            confidence += 0.2
        
        # Increase confidence if clinical significance is known
        if variant.get('Clinical_Significance') and variant['Clinical_Significance'] != 'Unknown':
            confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _generate_mock_explanation(self, variant: Dict[str, Any], similar_variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate mock explanation when LLM is not available."""
        
        gene = variant.get('Gene', 'Unknown gene')
        consequence = variant.get('Consequence', 'variant')
        clin_sig = variant.get('Clinical_Significance', 'uncertain significance')
        
        # Generate explanation based on consequence type
        if 'stop_gained' in consequence:
            explanation = f"This variant in {gene} introduces a premature stop codon, likely resulting in a truncated protein with reduced or abolished function. Such nonsense variants are typically associated with loss of gene function."
        
        elif 'frameshift' in consequence:
            explanation = f"This frameshift variant in {gene} alters the reading frame, likely producing an abnormal protein. Frameshift variants typically result in loss of normal protein function."
        
        elif 'missense' in consequence:
            explanation = f"This missense variant in {gene} changes an amino acid in the protein sequence. The functional impact depends on the specific amino acid change and its location in the protein structure."
        
        elif 'splice' in consequence:
            explanation = f"This splice site variant in {gene} may affect normal RNA splicing, potentially leading to altered protein production or function."
        
        else:
            explanation = f"This {consequence} in {gene} has {clin_sig}. Further functional studies may be needed to determine its clinical impact."
        
        # Add context from similar variants
        if similar_variants:
            pathogenic_count = sum(1 for v in similar_variants if 'pathogenic' in v.get('clinical_significance', '').lower())
            if pathogenic_count > 0:
                explanation += f" Similar variants in this gene have been associated with disease, supporting potential clinical relevance."
        
        explanation += " This interpretation is based on computational analysis and should be confirmed through clinical evaluation."
        
        return {
            'variant_id': variant.get('Variant_ID', ''),
            'gene': gene,
            'consequence': consequence,
            'explanation': explanation,
            'confidence_score': 0.6,  # Mock confidence
            'evidence_count': len(similar_variants),
            'similar_variants': [v.get('variation_id', '') for v in similar_variants[:3]],
            'clinical_significance': clin_sig,
            'pathogenicity_score': variant.get('Pathogenicity_Score', 0),
            'databases_used': ['ClinVar', 'gnomAD', 'Ensembl VEP'],
            'disclaimers': [
                "This analysis is for research purposes only and should not be used for medical diagnosis.",
                "Consult with a qualified healthcare provider for clinical interpretation.",
                "Variant interpretation may change as new evidence becomes available."
            ]
        }
    
    def _generate_fallback_explanation(self, variant: Dict[str, Any], similar_variants: List[Dict[str, Any]]) -> str:
        """Generate fallback explanation when LLM fails."""
        
        gene = variant.get('Gene', 'Unknown')
        consequence = variant.get('Consequence', 'variant')
        
        explanation = f"This {consequence} in the {gene} gene requires further evaluation. "
        
        if similar_variants:
            explanation += f"Analysis of {len(similar_variants)} similar variants suggests potential clinical relevance. "
        
        explanation += "Consult clinical genetics resources for detailed interpretation."
        
        return explanation


def summarize_variants(variants_file: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI explanations for all variants in a file.
    
    Args:
        variants_file: Path to annotated variants file
        config: Configuration dictionary
        
    Returns:
        Dictionary of explanations for each variant
    """
    logger.info(f"Generating AI explanations for variants in: {variants_file}")
    
    # Retrieve similar variants
    similar_variants_dict = retrieve_similar_variants(variants_file, config)
    
    # Filter retrieved variants
    filtered_variants = filter_retrieved_variants(similar_variants_dict, config)
    
    # Initialize summarizer
    summarizer = VariantSummarizer(config)
    
    # Load original variants
    if variants_file.endswith('.parquet'):
        df = pd.read_parquet(variants_file)
    else:
        df = pd.read_csv(variants_file, sep='\t')
    
    # Generate explanations
    explanations = {}
    
    for _, variant_row in df.iterrows():
        variant_dict = variant_row.to_dict()
        variant_id = variant_dict.get('Variant_ID', f"variant_{len(explanations)}")
        
        # Get similar variants for this variant
        similar_variants = filtered_variants.get(variant_id, [])
        
        # Generate explanation
        try:
            explanation = summarizer.generate_explanation(variant_dict, similar_variants)
            explanations[variant_id] = explanation
            
        except Exception as e:
            logger.error(f"Failed to generate explanation for {variant_id}: {e}")
            # Create minimal explanation
            explanations[variant_id] = {
                'variant_id': variant_id,
                'gene': variant_dict.get('Gene', ''),
                'explanation': f"Explanation generation failed for this variant. Manual review recommended.",
                'confidence_score': 0.0,
                'evidence_count': 0,
                'error': str(e)
            }
    
    logger.info(f"Generated explanations for {len(explanations)} variants")
    return explanations


def batch_explain_variants(
    variants_list: List[Dict[str, Any]], 
    config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate explanations for a list of variants.
    
    Args:
        variants_list: List of variant dictionaries
        config: Configuration dictionary
        
    Returns:
        List of explanation dictionaries
    """
    logger.info(f"Batch explaining {len(variants_list)} variants")
    
    summarizer = VariantSummarizer(config)
    explanations = []
    
    for variant in variants_list:
        # For batch processing, we skip similarity search for efficiency
        # In a full implementation, this could be optimized with batch retrieval
        explanation = summarizer.generate_explanation(variant, [])
        explanations.append(explanation)
    
    return explanations


def save_explanations(explanations: Dict[str, Any], outdir: Path) -> None:
    """Save explanations to files."""
    
    logger.info("Saving variant explanations")
    
    # Save as JSON
    explanations_file = outdir / "variant_explanations.json"
    with open(explanations_file, 'w') as f:
        json.dump(explanations, f, indent=2, default=str)
    
    # Save as TSV for human readability
    explanations_list = []
    for variant_id, explanation in explanations.items():
        row = {
            'Variant_ID': variant_id,
            'Gene': explanation.get('gene', ''),
            'Consequence': explanation.get('consequence', ''),
            'Clinical_Significance': explanation.get('clinical_significance', ''),
            'Explanation': explanation.get('explanation', ''),
            'Confidence_Score': explanation.get('confidence_score', 0),
            'Evidence_Count': explanation.get('evidence_count', 0),
            'Similar_Variants': '; '.join(explanation.get('similar_variants', [])),
            'Databases_Used': '; '.join(explanation.get('databases_used', []))
        }
        explanations_list.append(row)
    
    if explanations_list:
        df = pd.DataFrame(explanations_list)
        tsv_file = outdir / "variant_explanations.tsv"
        df.to_csv(tsv_file, sep='\t', index=False)
    
    logger.info(f"Explanations saved to {outdir}")