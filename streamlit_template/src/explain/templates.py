"""
Prompt templates for LLM-based variant explanation generation.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_explanation_template() -> str:
    """
    Get the main prompt template for variant explanation.
    
    Returns:
        Formatted prompt template string
    """
    
    template = """You are a clinical genetics expert providing educational information about genetic variants. 
Your task is to explain a genetic variant in clear, accessible language while maintaining scientific accuracy.

VARIANT INFORMATION:
{variant_context}

SIMILAR VARIANTS FROM DATABASE:
{similar_variants_context}

INSTRUCTIONS:
1. Provide a clear, 150-word explanation of this variant's potential significance
2. Explain what the {consequence} means in simple terms
3. Discuss the potential impact on the {gene} gene function
4. Reference similar variants when relevant
5. Include appropriate caveats about interpretation limitations
6. Use accessible language while maintaining scientific accuracy

IMPORTANT DISCLAIMERS TO INCLUDE:
- This is for research/educational purposes only
- Clinical interpretation requires professional evaluation
- Variant significance may change with new evidence

Please provide a concise, informative explanation:"""

    return template


def get_gene_context_template() -> str:
    """Get template for gene-specific context."""
    
    template = """The {gene} gene is located on chromosome {chromosome} and encodes a protein involved in {function}. 
Variants in this gene have been associated with {conditions}. The specific consequence type '{consequence}' 
typically results in {consequence_description}."""
    
    return template


def get_consequence_descriptions() -> Dict[str, str]:
    """Get descriptions for different variant consequence types."""
    
    descriptions = {
        'stop_gained': 'a premature stop codon that truncates the protein, usually resulting in loss of function',
        'frameshift_variant': 'a shift in the reading frame that alters all downstream amino acids, typically causing loss of function',
        'missense_variant': 'a change in one amino acid that may or may not affect protein function depending on the specific change',
        'splice_acceptor_variant': 'disruption of normal RNA splicing that may lead to abnormal protein production',
        'splice_donor_variant': 'disruption of normal RNA splicing that may lead to abnormal protein production',
        'synonymous_variant': 'a change that does not alter the amino acid sequence, usually having minimal functional impact',
        'inframe_deletion': 'removal of amino acids without shifting the reading frame, with variable functional impact',
        'inframe_insertion': 'addition of amino acids without shifting the reading frame, with variable functional impact',
        'start_lost': 'loss of the start codon that prevents normal protein production',
        'stop_lost': 'loss of the stop codon that may result in an extended protein with altered function',
        'transcript_ablation': 'complete loss of the transcript, resulting in absence of the protein',
        'regulatory_region_variant': 'a change in regulatory sequences that may affect gene expression levels',
        'intron_variant': 'a change within an intron that typically has minimal direct effect on protein function',
        'upstream_gene_variant': 'a change upstream of the gene that may affect gene regulation',
        'downstream_gene_variant': 'a change downstream of the gene that may affect gene regulation',
        '3_prime_UTR_variant': 'a change in the 3\' untranslated region that may affect mRNA stability or translation',
        '5_prime_UTR_variant': 'a change in the 5\' untranslated region that may affect translation initiation'
    }
    
    return descriptions


def get_clinical_significance_context() -> Dict[str, str]:
    """Get context for different clinical significance categories."""
    
    contexts = {
        'Pathogenic': 'This variant is established as disease-causing with strong evidence from multiple sources.',
        'Likely pathogenic': 'This variant is very likely to be disease-causing based on available evidence.',
        'Uncertain significance': 'The clinical significance of this variant is currently unclear and requires further study.',
        'Likely benign': 'This variant is probably not disease-causing based on current evidence.',
        'Benign': 'This variant is established as not disease-causing.',
        'risk factor': 'This variant increases disease risk but is not directly causative.',
        'drug response': 'This variant affects response to specific medications.',
        'protective': 'This variant may provide protection against certain conditions.',
        'conflicting interpretations': 'Different sources provide conflicting assessments of this variant\'s significance.'
    }
    
    return contexts


def format_variant_context(variant: Dict[str, Any]) -> str:
    """
    Format variant information for prompt context.
    
    Args:
        variant: Variant information dictionary
        
    Returns:
        Formatted context string
    """
    
    context_parts = []
    
    # Basic variant information
    if variant.get('Variant_ID'):
        context_parts.append(f"Variant ID: {variant['Variant_ID']}")
    
    if variant.get('Gene'):
        context_parts.append(f"Gene: {variant['Gene']}")
    
    if variant.get('Genomic_Position'):
        context_parts.append(f"Position: {variant['Genomic_Position']}")
    
    if variant.get('Consequence'):
        context_parts.append(f"Consequence: {variant['Consequence']}")
        
        # Add consequence description
        descriptions = get_consequence_descriptions()
        if variant['Consequence'] in descriptions:
            context_parts.append(f"Consequence meaning: {descriptions[variant['Consequence']]}")
    
    # Clinical significance
    if variant.get('Clinical_Significance'):
        context_parts.append(f"Clinical significance: {variant['Clinical_Significance']}")
        
        # Add clinical significance context
        clin_contexts = get_clinical_significance_context()
        clin_sig = variant['Clinical_Significance']
        if clin_sig in clin_contexts:
            context_parts.append(f"Significance meaning: {clin_contexts[clin_sig]}")
    
    # Protein impact
    if variant.get('Protein_position'):
        context_parts.append(f"Protein position: {variant['Protein_position']}")
    
    if variant.get('Amino_acids'):
        context_parts.append(f"Amino acid change: {variant['Amino_acids']}")
    
    # Population frequency
    if variant.get('gnomAD_AF'):
        freq = float(variant['gnomAD_AF'])
        if freq > 0:
            context_parts.append(f"Population frequency: {freq:.6f} ({freq*100:.4f}%)")
        else:
            context_parts.append("Population frequency: Not found in gnomAD")
    
    # Impact level
    if variant.get('IMPACT'):
        context_parts.append(f"Impact level: {variant['IMPACT']}")
    
    # Existing variation IDs
    if variant.get('dbSNP_ID') and variant['dbSNP_ID'] != '.':
        context_parts.append(f"dbSNP ID: {variant['dbSNP_ID']}")
    
    # ClinVar information
    if variant.get('ClinVar_ID'):
        context_parts.append(f"ClinVar ID: {variant['ClinVar_ID']}")
    
    if variant.get('ClinVar_Conditions'):
        context_parts.append(f"Associated conditions: {variant['ClinVar_Conditions']}")
    
    return '\n'.join(context_parts)


def get_report_template() -> str:
    """Get template for variant explanation report section."""
    
    template = """
## AI-Powered Variant Explanations

The following explanations were generated using artificial intelligence analysis of variant annotations 
and similarity to known variants in clinical databases.

**Important Disclaimers:**
- These explanations are for research and educational purposes only
- Clinical interpretation should always be performed by qualified healthcare professionals
- Variant classifications may change as new evidence becomes available
- This analysis does not constitute medical advice

### Methodology
Explanations were generated by:
1. Comparing variants to a curated database of clinically characterized variants
2. Using semantic similarity search to find related variants
3. Applying natural language processing to generate human-readable explanations
4. Incorporating evidence from ClinVar, gnomAD, and Ensembl VEP annotations

---

{variant_explanations}

---

**Analysis Summary:**
- Total variants explained: {total_variants}
- Average confidence score: {avg_confidence:.2f}
- High-confidence explanations (>0.8): {high_confidence_count}
- Variants with database evidence: {evidence_count}

**Databases Used:**
- ClinVar: Clinical variant interpretations
- gnomAD: Population allele frequencies  
- Ensembl VEP: Functional annotations
- FAISS: Similarity search index

For questions about specific variants, consult with a clinical geneticist or genetic counselor.
"""
    
    return template


def format_explanation_for_report(explanation: Dict[str, Any]) -> str:
    """
    Format a single explanation for inclusion in report.
    
    Args:
        explanation: Explanation dictionary
        
    Returns:
        Formatted explanation string
    """
    
    output = []
    
    # Header
    gene = explanation.get('gene', 'Unknown')
    variant_id = explanation.get('variant_id', 'Unknown')
    output.append(f"### {gene} Variant ({variant_id})")
    
    # Basic information
    consequence = explanation.get('consequence', 'Unknown')
    clin_sig = explanation.get('clinical_significance', 'Unknown')
    output.append(f"**Type:** {consequence}")
    output.append(f"**Clinical Significance:** {clin_sig}")
    
    # Confidence and evidence
    confidence = explanation.get('confidence_score', 0)
    evidence_count = explanation.get('evidence_count', 0)
    output.append(f"**Confidence Score:** {confidence:.2f}/1.0")
    output.append(f"**Supporting Evidence:** {evidence_count} similar variants")
    
    # Main explanation
    explanation_text = explanation.get('explanation', 'No explanation available.')
    output.append(f"\n**Explanation:**\n{explanation_text}")
    
    # Similar variants
    similar_variants = explanation.get('similar_variants', [])
    if similar_variants:
        output.append(f"\n**Related Variants:** {', '.join(similar_variants[:3])}")
    
    # Disclaimers
    disclaimers = explanation.get('disclaimers', [])
    if disclaimers:
        output.append(f"\n**Important Notes:**")
        for disclaimer in disclaimers:
            output.append(f"- {disclaimer}")
    
    output.append("\n---\n")
    
    return '\n'.join(output)


def get_summary_template() -> str:
    """Get template for explanation summary section."""
    
    template = """
## Explanation Summary

**Analysis Overview:**
- Total variants analyzed: {total_variants}
- Variants with high-confidence explanations: {high_confidence}
- Average confidence score: {avg_confidence:.2f}
- Most common variant types: {top_consequences}
- Most frequently affected genes: {top_genes}

**Quality Metrics:**
- Explanations with database evidence: {with_evidence}%
- Average similarity to known variants: {avg_similarity:.2f}
- Explanations requiring manual review: {low_confidence}

**Recommendations:**
- Variants with confidence < 0.5 should undergo manual review
- High-impact variants should be validated experimentally
- Clinical correlation is essential for all interpretations
"""
    
    return template