"""
Report generation module using Jinja2 templates for HTML and Markdown output.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

import pandas as pd
from jinja2 import Environment, FileSystemLoader, Template

from .explain.templates import get_report_template, format_explanation_for_report

logger = logging.getLogger(__name__)


def generate_report(
    variants_file: Optional[str],
    rna_output: Optional[str], 
    outdir: Path, 
    config: Dict[str, Any],
    explanations: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate comprehensive analysis report.
    
    Args:
        variants_file: Path to annotated variants file
        rna_output: Path to RNA-seq results directory
        outdir: Output directory for report
        config: Configuration dictionary
        explanations: Optional variant explanations dictionary
        
    Returns:
        Path to generated report
    """
    logger.info("Generating analysis report")
    
    # Create report directory
    report_dir = outdir / "report"
    report_dir.mkdir(exist_ok=True)
    
    # Collect data for report
    report_data = _collect_report_data(variants_file, rna_output, config, explanations)
    
    # Generate HTML report
    html_report = _generate_html_report(report_data, report_dir, config)
    
    # Generate Markdown report
    md_report = _generate_markdown_report(report_data, report_dir, config)
    
    # Generate summary files
    _generate_summary_files(report_data, report_dir)
    
    logger.info(f"Reports generated in {report_dir}")
    return str(html_report)


def _collect_report_data(
    variants_file: Optional[str],
    rna_output: Optional[str],
    config: Dict[str, Any],
    explanations: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Collect all data needed for report generation."""
    
    logger.info("Collecting report data")
    
    report_data = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'genomeai_version': '1.0.0',
            'config_used': config,
            'analysis_type': []
        },
        'variants': None,
        'rna': None,
        'explanations': explanations or {},
        'summary': {}
    }
    
    # Load variant data
    if variants_file and Path(variants_file).exists():
        report_data['metadata']['analysis_type'].append('DNA Variant Analysis')
        report_data['variants'] = _load_variant_data(variants_file)
    
    # Load RNA data
    if rna_output and Path(rna_output).exists():
        report_data['metadata']['analysis_type'].append('RNA-seq Analysis')
        report_data['rna'] = _load_rna_data(rna_output)
    
    # Generate summary statistics
    report_data['summary'] = _generate_summary_stats(report_data)
    
    return report_data


def _load_variant_data(variants_file: str) -> Dict[str, Any]:
    """Load and process variant data for reporting."""
    
    logger.info(f"Loading variant data from {variants_file}")
    
    try:
        if variants_file.endswith('.parquet'):
            df = pd.read_parquet(variants_file)
        else:
            df = pd.read_csv(variants_file, sep='\t')
        
        # Process variant data
        variant_data = {
            'total_variants': len(df),
            'dataframe': df,
            'top_variants': df.head(20).to_dict('records') if not df.empty else [],
            'consequence_counts': {},
            'impact_distribution': {},
            'clinical_significance_counts': {},
            'top_genes': {}
        }
        
        if not df.empty:
            # Consequence distribution
            if 'Consequence' in df.columns:
                consequence_counts = df['Consequence'].value_counts().head(10).to_dict()
                variant_data['consequence_counts'] = consequence_counts
            
            # Impact distribution
            if 'IMPACT' in df.columns:
                impact_counts = df['IMPACT'].value_counts().to_dict()
                variant_data['impact_distribution'] = impact_counts
            
            # Clinical significance
            if 'Clinical_Significance' in df.columns:
                clin_sig_counts = df['Clinical_Significance'].value_counts().to_dict()
                variant_data['clinical_significance_counts'] = clin_sig_counts
            
            # Top genes
            if 'Gene' in df.columns:
                top_genes = df['Gene'].value_counts().head(10).to_dict()
                variant_data['top_genes'] = top_genes
        
        return variant_data
        
    except Exception as e:
        logger.error(f"Failed to load variant data: {e}")
        return {'total_variants': 0, 'dataframe': pd.DataFrame(), 'error': str(e)}


def _load_rna_data(rna_output: str) -> Dict[str, Any]:
    """Load and process RNA-seq data for reporting."""
    
    logger.info(f"Loading RNA data from {rna_output}")
    
    rna_dir = Path(rna_output)
    rna_data = {
        'quantification_available': False,
        'total_features': 0,
        'expressed_features': 0,
        'top_expressed': [],
        'expression_stats': {}
    }
    
    try:
        # Load expression summary
        summary_file = rna_dir / "expression_summary.tsv"
        if summary_file.exists():
            df = pd.read_csv(summary_file, sep='\t')
            rna_data['quantification_available'] = True
            rna_data['total_features'] = len(df)
            
            if 'TPM' in df.columns:
                expressed_df = df[df['TPM'] >= 1]
                rna_data['expressed_features'] = len(expressed_df)
                
                # Top expressed features
                top_expressed = df.nlargest(20, 'TPM')
                rna_data['top_expressed'] = top_expressed.to_dict('records')
        
        # Load expression statistics
        stats_file = rna_dir / "expression_stats.json"
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                rna_data['expression_stats'] = json.load(f)
        
        return rna_data
        
    except Exception as e:
        logger.error(f"Failed to load RNA data: {e}")
        rna_data['error'] = str(e)
        return rna_data


def _generate_summary_stats(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate overall summary statistics."""
    
    summary = {
        'analysis_complete': True,
        'total_variants': 0,
        'high_impact_variants': 0,
        'pathogenic_variants': 0,
        'total_genes_with_variants': 0,
        'rna_features_quantified': 0,
        'explanations_generated': 0,
        'high_confidence_explanations': 0
    }
    
    # Variant statistics
    if report_data['variants']:
        variant_data = report_data['variants']
        summary['total_variants'] = variant_data.get('total_variants', 0)
        
        df = variant_data.get('dataframe')
        if df is not None and not df.empty:
            # High impact variants
            if 'IMPACT' in df.columns:
                high_impact = df[df['IMPACT'] == 'HIGH']
                summary['high_impact_variants'] = len(high_impact)
            
            # Pathogenic variants
            if 'Clinical_Significance' in df.columns:
                pathogenic = df[df['Clinical_Significance'].str.contains('Pathogenic', na=False)]
                summary['pathogenic_variants'] = len(pathogenic)
            
            # Unique genes
            if 'Gene' in df.columns:
                unique_genes = df['Gene'].nunique()
                summary['total_genes_with_variants'] = unique_genes
    
    # RNA statistics
    if report_data['rna']:
        rna_data = report_data['rna']
        summary['rna_features_quantified'] = rna_data.get('expressed_features', 0)
    
    # Explanation statistics
    if report_data['explanations']:
        explanations = report_data['explanations']
        summary['explanations_generated'] = len(explanations)
        
        high_conf_count = sum(1 for exp in explanations.values() 
                             if exp.get('confidence_score', 0) >= 0.8)
        summary['high_confidence_explanations'] = high_conf_count
    
    return summary


def _generate_html_report(report_data: Dict[str, Any], report_dir: Path, config: Dict[str, Any]) -> Path:
    """Generate HTML report."""
    
    logger.info("Generating HTML report")
    
    html_template = _get_html_template()
    
    # Render template
    template = Template(html_template)
    html_content = template.render(
        report_data=report_data,
        config=config,
        datetime=datetime
    )
    
    # Save HTML report
    html_file = report_dir / "genomeai_report.html"
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"HTML report saved to {html_file}")
    return html_file


def _generate_markdown_report(report_data: Dict[str, Any], report_dir: Path, config: Dict[str, Any]) -> Path:
    """Generate Markdown report."""
    
    logger.info("Generating Markdown report")
    
    md_content = []
    
    # Header
    md_content.append("# GenomeAI Analysis Report")
    md_content.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_content.append(f"**GenomeAI Version:** {report_data['metadata']['genomeai_version']}")
    md_content.append(f"**Analysis Type:** {', '.join(report_data['metadata']['analysis_type'])}")
    
    # Executive Summary
    md_content.append("\n## Executive Summary")
    summary = report_data['summary']
    md_content.append(f"- **Total Variants Analyzed:** {summary['total_variants']}")
    md_content.append(f"- **High-Impact Variants:** {summary['high_impact_variants']}")
    md_content.append(f"- **Pathogenic/Likely Pathogenic:** {summary['pathogenic_variants']}")
    md_content.append(f"- **Genes with Variants:** {summary['total_genes_with_variants']}")
    
    if summary['rna_features_quantified'] > 0:
        md_content.append(f"- **RNA Features Quantified:** {summary['rna_features_quantified']}")
    
    if summary['explanations_generated'] > 0:
        md_content.append(f"- **AI Explanations Generated:** {summary['explanations_generated']}")
        md_content.append(f"- **High-Confidence Explanations:** {summary['high_confidence_explanations']}")
    
    # Variant Analysis Section
    if report_data['variants']:
        md_content.append("\n## Variant Analysis")
        variant_data = report_data['variants']
        
        md_content.append(f"\n### Summary Statistics")
        md_content.append(f"- Total variants: {variant_data['total_variants']}")
        
        # Consequence distribution
        if variant_data['consequence_counts']:
            md_content.append(f"\n### Top Variant Consequences")
            for consequence, count in list(variant_data['consequence_counts'].items())[:5]:
                md_content.append(f"- {consequence}: {count}")
        
        # Impact distribution
        if variant_data['impact_distribution']:
            md_content.append(f"\n### Impact Distribution")
            for impact, count in variant_data['impact_distribution'].items():
                md_content.append(f"- {impact}: {count}")
        
        # Top genes
        if variant_data['top_genes']:
            md_content.append(f"\n### Most Frequently Affected Genes")
            for gene, count in list(variant_data['top_genes'].items())[:10]:
                md_content.append(f"- {gene}: {count} variants")
        
        # Top variants table
        if variant_data['top_variants']:
            md_content.append(f"\n### Top Priority Variants")
            md_content.append("| Gene | Consequence | Clinical Significance | Impact |")
            md_content.append("|------|-------------|----------------------|--------|")
            
            for variant in variant_data['top_variants'][:10]:
                gene = variant.get('Gene', 'Unknown')
                consequence = variant.get('Consequence', 'Unknown')
                clin_sig = variant.get('Clinical_Significance', 'Unknown')
                impact = variant.get('IMPACT', 'Unknown')
                md_content.append(f"| {gene} | {consequence} | {clin_sig} | {impact} |")
    
    # RNA Analysis Section
    if report_data['rna'] and report_data['rna']['quantification_available']:
        md_content.append("\n## RNA-seq Analysis")
        rna_data = report_data['rna']
        
        md_content.append(f"- Total features: {rna_data['total_features']}")
        md_content.append(f"- Expressed features (TPM ≥ 1): {rna_data['expressed_features']}")
        
        if rna_data['expression_stats']:
            stats = rna_data['expression_stats']
            md_content.append(f"- Median TPM: {stats.get('median_tpm', 0):.2f}")
            md_content.append(f"- Mean TPM: {stats.get('mean_tpm', 0):.2f}")
        
        # Top expressed features
        if rna_data['top_expressed']:
            md_content.append(f"\n### Top Expressed Features")
            md_content.append("| Feature | TPM | Reads |")
            md_content.append("|---------|-----|-------|")
            
            for feature in rna_data['top_expressed'][:10]:
                name = feature.get('Name', 'Unknown')
                tpm = feature.get('TPM', 0)
                reads = feature.get('NumReads', 0)
                md_content.append(f"| {name} | {tpm:.2f} | {reads} |")
    
    # AI Explanations Section
    if report_data['explanations']:
        md_content.append("\n## AI-Powered Variant Explanations")
        md_content.append("\n**Disclaimer:** These explanations are for research purposes only and should not be used for medical diagnosis. Consult with qualified healthcare professionals for clinical interpretation.")
        
        explanations = report_data['explanations']
        
        # Sort by confidence score
        sorted_explanations = sorted(
            explanations.items(), 
            key=lambda x: x[1].get('confidence_score', 0), 
            reverse=True
        )
        
        for variant_id, explanation in sorted_explanations[:10]:  # Top 10
            md_content.append(f"\n### {explanation.get('gene', 'Unknown')} Variant")
            md_content.append(f"**Variant ID:** {variant_id}")
            md_content.append(f"**Consequence:** {explanation.get('consequence', 'Unknown')}")
            md_content.append(f"**Clinical Significance:** {explanation.get('clinical_significance', 'Unknown')}")
            md_content.append(f"**Confidence Score:** {explanation.get('confidence_score', 0):.2f}")
            
            explanation_text = explanation.get('explanation', 'No explanation available.')
            md_content.append(f"\n**Explanation:** {explanation_text}")
            
            if explanation.get('similar_variants'):
                similar = ', '.join(explanation['similar_variants'][:3])
                md_content.append(f"\n**Similar Variants:** {similar}")
    
    # Methods Section
    md_content.append("\n## Methods")
    md_content.append("### Pipeline Overview")
    md_content.append("1. **Quality Control:** fastp for read trimming and quality assessment")
    md_content.append("2. **Alignment:** bwa-mem2 (Illumina) or minimap2 (Nanopore) to GRCh38")
    md_content.append("3. **Variant Calling:** FreeBayes with quality filters")
    md_content.append("4. **Annotation:** Ensembl VEP with ClinVar and gnomAD databases")
    md_content.append("5. **AI Explanation:** Similarity search with local LLM summarization")
    
    if report_data['rna']:
        md_content.append("6. **RNA Quantification:** Salmon for transcript-level quantification")
    
    # Configuration
    md_content.append("\n### Configuration Parameters")
    key_params = [
        'threads', 'qc', 'variant_calling', 'variant_filtering', 'annotation'
    ]
    
    for param in key_params:
        if param in config:
            md_content.append(f"- **{param}:** {config[param]}")
    
    # Footer
    md_content.append(f"\n---")
    md_content.append(f"\n*Report generated by GenomeAI v{report_data['metadata']['genomeai_version']} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    md_content.append(f"\n*For questions or support, please refer to the GenomeAI documentation.*")
    
    # Save Markdown report
    md_file = report_dir / "genomeai_report.md"
    with open(md_file, 'w') as f:
        f.write('\n'.join(md_content))
    
    logger.info(f"Markdown report saved to {md_file}")
    return md_file


def _generate_summary_files(report_data: Dict[str, Any], report_dir: Path) -> None:
    """Generate additional summary files."""
    
    logger.info("Generating summary files")
    
    # JSON summary
    summary_file = report_dir / "analysis_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(report_data['summary'], f, indent=2, default=str)
    
    # Variant summary CSV
    if report_data['variants'] and not report_data['variants']['dataframe'].empty:
        df = report_data['variants']['dataframe']
        
        # Create simplified summary
        summary_cols = ['Gene', 'Consequence', 'Clinical_Significance', 'IMPACT']
        available_cols = [col for col in summary_cols if col in df.columns]
        
        if available_cols:
            summary_df = df[available_cols].head(100)  # Top 100 variants
            csv_file = report_dir / "top_variants_summary.csv"
            summary_df.to_csv(csv_file, index=False)
    
    # RNA summary CSV
    if report_data['rna'] and report_data['rna']['top_expressed']:
        rna_df = pd.DataFrame(report_data['rna']['top_expressed'])
        rna_csv = report_dir / "top_expressed_features.csv"
        rna_df.to_csv(rna_csv, index=False)
    
    logger.info("Summary files generated")


def _get_html_template() -> str:
    """Get HTML template for report generation."""
    
    template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GenomeAI Analysis Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        h3 {
            color: #7f8c8d;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card h3 {
            color: white;
            margin: 0 0 10px 0;
        }
        .summary-card .number {
            font-size: 2em;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .disclaimer {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
        .explanation {
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 10px 0;
        }
        .confidence-high { color: #28a745; font-weight: bold; }
        .confidence-medium { color: #ffc107; font-weight: bold; }
        .confidence-low { color: #dc3545; font-weight: bold; }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>GenomeAI Analysis Report</h1>
        
        <div class="metadata">
            <p><strong>Generated:</strong> {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</p>
            <p><strong>GenomeAI Version:</strong> {{ report_data.metadata.genomeai_version }}</p>
            <p><strong>Analysis Type:</strong> {{ ', '.join(report_data.metadata.analysis_type) }}</p>
        </div>

        <h2>Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Variants</h3>
                <div class="number">{{ report_data.summary.total_variants }}</div>
            </div>
            <div class="summary-card">
                <h3>High-Impact Variants</h3>
                <div class="number">{{ report_data.summary.high_impact_variants }}</div>
            </div>
            <div class="summary-card">
                <h3>Pathogenic Variants</h3>
                <div class="number">{{ report_data.summary.pathogenic_variants }}</div>
            </div>
            {% if report_data.summary.explanations_generated > 0 %}
            <div class="summary-card">
                <h3>AI Explanations</h3>
                <div class="number">{{ report_data.summary.explanations_generated }}</div>
            </div>
            {% endif %}
        </div>

        {% if report_data.variants %}
        <h2>Variant Analysis</h2>
        <h3>Top Priority Variants</h3>
        <table>
            <thead>
                <tr>
                    <th>Gene</th>
                    <th>Consequence</th>
                    <th>Clinical Significance</th>
                    <th>Impact</th>
                </tr>
            </thead>
            <tbody>
                {% for variant in report_data.variants.top_variants[:10] %}
                <tr>
                    <td>{{ variant.get('Gene', 'Unknown') }}</td>
                    <td>{{ variant.get('Consequence', 'Unknown') }}</td>
                    <td>{{ variant.get('Clinical_Significance', 'Unknown') }}</td>
                    <td>{{ variant.get('IMPACT', 'Unknown') }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        {% if report_data.explanations %}
        <h2>AI-Powered Variant Explanations</h2>
        <div class="disclaimer">
            <strong>Important Disclaimer:</strong> These explanations are for research purposes only and should not be used for medical diagnosis. 
            Consult with qualified healthcare professionals for clinical interpretation.
        </div>
        
        {% for variant_id, explanation in report_data.explanations.items() %}
        {% if loop.index <= 5 %}
        <div class="explanation">
            <h3>{{ explanation.get('gene', 'Unknown') }} Variant ({{ variant_id }})</h3>
            <p><strong>Consequence:</strong> {{ explanation.get('consequence', 'Unknown') }}</p>
            <p><strong>Clinical Significance:</strong> {{ explanation.get('clinical_significance', 'Unknown') }}</p>
            <p><strong>Confidence Score:</strong> 
                {% set confidence = explanation.get('confidence_score', 0) %}
                <span class="{% if confidence >= 0.8 %}confidence-high{% elif confidence >= 0.5 %}confidence-medium{% else %}confidence-low{% endif %}">
                    {{ "%.2f"|format(confidence) }}
                </span>
            </p>
            <p><strong>Explanation:</strong> {{ explanation.get('explanation', 'No explanation available.') }}</p>
        </div>
        {% endif %}
        {% endfor %}
        {% endif %}

        {% if report_data.rna and report_data.rna.quantification_available %}
        <h2>RNA-seq Analysis</h2>
        <p><strong>Total Features:</strong> {{ report_data.rna.total_features }}</p>
        <p><strong>Expressed Features (TPM ≥ 1):</strong> {{ report_data.rna.expressed_features }}</p>
        
        {% if report_data.rna.top_expressed %}
        <h3>Top Expressed Features</h3>
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th>TPM</th>
                    <th>Reads</th>
                </tr>
            </thead>
            <tbody>
                {% for feature in report_data.rna.top_expressed[:10] %}
                <tr>
                    <td>{{ feature.get('Name', 'Unknown') }}</td>
                    <td>{{ "%.2f"|format(feature.get('TPM', 0)) }}</td>
                    <td>{{ feature.get('NumReads', 0) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
        {% endif %}

        <h2>Methods</h2>
        <h3>Pipeline Overview</h3>
        <ol>
            <li><strong>Quality Control:</strong> fastp for read trimming and quality assessment</li>
            <li><strong>Alignment:</strong> bwa-mem2 (Illumina) or minimap2 (Nanopore) to GRCh38</li>
            <li><strong>Variant Calling:</strong> FreeBayes with quality filters</li>
            <li><strong>Annotation:</strong> Ensembl VEP with ClinVar and gnomAD databases</li>
            <li><strong>AI Explanation:</strong> Similarity search with local LLM summarization</li>
            {% if report_data.rna %}
            <li><strong>RNA Quantification:</strong> Salmon for transcript-level quantification</li>
            {% endif %}
        </ol>

        <div class="footer">
            <p>Report generated by GenomeAI v{{ report_data.metadata.genomeai_version }}</p>
            <p>For questions or support, please refer to the GenomeAI documentation.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return template


def create_custom_report(
    template_file: str, 
    report_data: Dict[str, Any], 
    output_file: str
) -> None:
    """
    Generate report using custom template.
    
    Args:
        template_file: Path to custom Jinja2 template
        report_data: Report data dictionary
        output_file: Output file path
    """
    logger.info(f"Generating custom report using template: {template_file}")
    
    try:
        # Load custom template
        template_path = Path(template_file)
        env = Environment(loader=FileSystemLoader(template_path.parent))
        template = env.get_template(template_path.name)
        
        # Render template
        content = template.render(report_data=report_data, datetime=datetime)
        
        # Save output
        with open(output_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Custom report saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Failed to generate custom report: {e}")
        raise RuntimeError(f"Custom report generation failed: {e}")