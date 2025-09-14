"""
Enhanced report generation module that combines all analysis results.
Generates comprehensive reports including pharmacogenomics, MTHFR, disease risk, and traits.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class EnhancedReportGenerator:
    """Enhanced report generator for comprehensive genomics analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize enhanced report generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def generate_comprehensive_report(self, outdir: Path, results: Dict[str, Any]) -> str:
        """
        Generate comprehensive report combining all analysis modules.
        
        Args:
            outdir: Output directory
            results: Combined results from all analysis modules
            
        Returns:
            Path to generated comprehensive report
        """
        logger.info("Generating comprehensive genomics report")
        
        report_content = []
        
        # Header and disclaimers
        report_content.extend(self._generate_header())
        
        # Executive summary
        report_content.extend(self._generate_executive_summary(results))
        
        # Pharmacogenomics section
        if 'pharmacogenomics' in results:
            report_content.extend(self._generate_pharmacogenomics_section(results['pharmacogenomics']))
        
        # MTHFR section
        if 'mthfr' in results:
            report_content.extend(self._generate_mthfr_section(results['mthfr']))
        
        # Disease risk section
        if 'disease_risk' in results:
            report_content.extend(self._generate_disease_risk_section(results['disease_risk']))
        
        # Traits and ancestry section
        if 'traits_ancestry' in results:
            report_content.extend(self._generate_traits_section(results['traits_ancestry']))
        
        # Variant details section
        if 'variant_details' in results:
            report_content.extend(self._generate_variant_details_section(results['variant_details']))
        
        # Recommendations and next steps
        report_content.extend(self._generate_recommendations_section(results))
        
        # Footer
        report_content.extend(self._generate_footer())
        
        # Save comprehensive report
        report_file = outdir / "comprehensive_genomics_report.md"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_content))
        
        # Also generate HTML version
        html_file = self._generate_html_report(report_content, outdir)
        
        logger.info(f"Comprehensive report saved to {report_file}")
        return str(report_file)
    
    def _generate_header(self) -> List[str]:
        """Generate report header with disclaimers."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return [
            "# Comprehensive Genomics Analysis Report",
            f"\n**Generated**: {timestamp}",
            f"**Platform**: GenomeAI Enhanced Pipeline",
            "\n## 🚨 CRITICAL MEDICAL DISCLAIMER",
            "**THIS ANALYSIS IS FOR RESEARCH AND EDUCATIONAL PURPOSES ONLY**",
            "\n**Important Notice**: This genetic analysis is NOT intended for medical diagnosis, treatment, or clinical decision-making. The information provided should not replace professional medical advice, diagnosis, or treatment. Genetic variants have complex interactions with environmental factors, and individual responses vary significantly.",
            "\n**Before acting on any information in this report**:",
            "- Consult with qualified healthcare providers",
            "- Seek genetic counseling for significant findings",
            "- Understand that genetic predisposition ≠ certainty of disease",
            "- Consider family history and lifestyle factors",
            "- Verify findings through clinical-grade testing when appropriate",
            "\n---"
        ]
    
    def _generate_executive_summary(self, results: Dict[str, Any]) -> List[str]:
        """Generate executive summary of all findings."""
        summary_content = ["\n## Executive Summary"]
        
        # Count findings across all modules
        high_priority_findings = []
        moderate_findings = []
        actionable_findings = []
        
        # Pharmacogenomics findings
        if 'pharmacogenomics' in results:
            pharmaco_summary = results['pharmacogenomics'].get('summary', {})
            high_risk = pharmaco_summary.get('high_risk_findings', [])
            moderate_risk = pharmaco_summary.get('moderate_risk_findings', [])
            high_priority_findings.extend([f"Pharmacogenomics: {finding}" for finding in high_risk])
            moderate_findings.extend([f"Pharmacogenomics: {finding}" for finding in moderate_risk])
        
        # MTHFR findings
        if 'mthfr' in results:
            mthfr_combined = results['mthfr'].get('combined_analysis', {})
            risk_level = mthfr_combined.get('risk_level', 'Low')
            if risk_level == 'High':
                high_priority_findings.append(f"MTHFR: High-risk variant combination")
            elif risk_level in ['Moderate', 'Mild']:
                moderate_findings.append(f"MTHFR: {risk_level} risk variant(s)")
        
        # Disease risk findings
        if 'disease_risk' in results:
            disease_summary = results['disease_risk'].get('summary', {})
            high_risk = disease_summary.get('high_risk_findings', [])
            moderate_risk = disease_summary.get('moderate_risk_findings', [])
            high_priority_findings.extend([f"Disease Risk: {finding}" for finding in high_risk])
            moderate_findings.extend([f"Disease Risk: {finding}" for finding in moderate_risk])
        
        # Traits findings
        if 'traits_ancestry' in results:
            traits_summary = results['traits_ancestry'].get('summary', {})
            actionable = traits_summary.get('actionable_findings', [])
            actionable_findings.extend([f"Traits: {finding}" for finding in actionable])
        
        # Summary statistics
        summary_content.append(f"\n### Key Findings Overview")
        summary_content.append(f"- **High-Priority Findings**: {len(high_priority_findings)}")
        summary_content.append(f"- **Moderate-Risk Findings**: {len(moderate_findings)}")
        summary_content.append(f"- **Actionable Lifestyle Findings**: {len(actionable_findings)}")
        
        # High-priority findings
        if high_priority_findings:
            summary_content.append(f"\n### 🚨 High-Priority Findings (Require Immediate Attention)")
            for finding in high_priority_findings:
                summary_content.append(f"- **{finding}**")
            summary_content.append("\n*These findings warrant immediate consultation with healthcare providers and/or genetic counselors.*")
        
        # Moderate findings
        if moderate_findings:
            summary_content.append(f"\n### ⚠️ Moderate-Risk Findings")
            for finding in moderate_findings:
                summary_content.append(f"- {finding}")
        
        # Actionable findings
        if actionable_findings:
            summary_content.append(f"\n### 💡 Actionable Lifestyle Findings")
            for finding in actionable_findings:
                summary_content.append(f"- {finding}")
        
        return summary_content
    
    def _generate_pharmacogenomics_section(self, pharmaco_results: Dict[str, Any]) -> List[str]:
        """Generate pharmacogenomics section."""
        content = ["\n## Pharmacogenomics Analysis"]
        content.append("*Analysis of drug-gene interactions and metabolizer status*")
        
        summary = pharmaco_results.get('summary', {})
        content.append(f"\n**Genes Analyzed**: {summary.get('total_genes_analyzed', 0)}")
        content.append(f"**Drug Interactions Identified**: {summary.get('drug_interactions_identified', 0)}")
        
        # Key findings
        gene_order = ['cyp2d6', 'cyp2c19', 'tpmt', 'dpyd']
        
        for gene in gene_order:
            if gene in pharmaco_results:
                data = pharmaco_results[gene]
                if isinstance(data, dict):
                    content.append(f"\n### {data.get('gene', gene).upper()}")
                    content.append(f"**Phenotype**: {data.get('predicted_phenotype', 'normal')}")
                    content.append(f"**Clinical Significance**: {data.get('clinical_significance', '')}")
                    
                    drug_recs = data.get('drug_recommendations', {})
                    if drug_recs:
                        content.append("**Key Drug Recommendations**:")
                        for drug, rec in list(drug_recs.items())[:3]:  # Show top 3
                            content.append(f"- **{drug.title()}**: {rec}")
        
        content.append(f"\n*Full pharmacogenomics details available in separate report*")
        return content
    
    def _generate_mthfr_section(self, mthfr_results: Dict[str, Any]) -> List[str]:
        """Generate MTHFR section."""
        content = ["\n## MTHFR Gene Analysis"]
        content.append("*Analysis of folate metabolism variants C677T and A1298C*")
        
        combined = mthfr_results.get('combined_analysis', {})
        content.append(f"\n**Combined Genotype**: {combined.get('combined_genotype', 'Unknown')}")
        content.append(f"**Risk Level**: {combined.get('risk_level', 'Unknown')}")
        content.append(f"**Enzyme Efficiency**: {combined.get('enzyme_efficiency', 'Unknown')}")
        
        # Health implications
        implications = mthfr_results.get('health_implications', {})
        folate = implications.get('folate_metabolism', {})
        if folate:
            content.append(f"\n**Folate Metabolism Impact**: {folate.get('description', '')}")
            content.append(f"**Supplementation Need**: {folate.get('supplement_need', '')}")
        
        # Key recommendations
        recommendations = mthfr_results.get('recommendations', {})
        supplements = recommendations.get('supplementation', [])
        if supplements:
            content.append(f"\n**Key Recommendations**:")
            for rec in supplements[:3]:  # Show top 3
                content.append(f"- {rec}")
        
        content.append(f"\n*Full MTHFR analysis available in separate report*")
        return content
    
    def _generate_disease_risk_section(self, disease_results: Dict[str, Any]) -> List[str]:
        """Generate disease risk section."""
        content = ["\n## Disease Risk Analysis"]
        content.append("*Analysis of genetic variants associated with disease predisposition*")
        
        summary = disease_results.get('summary', {})
        content.append(f"\n**High-Risk Findings**: {len(summary.get('high_risk_findings', []))}")
        content.append(f"**Actionable Findings**: {summary.get('actionable_findings', 0)}")
        
        # BRCA analysis
        brca = disease_results.get('brca_analysis', {})
        if brca:
            content.append(f"\n### Hereditary Cancer Risk (BRCA1/BRCA2)")
            content.append(f"**Assessment**: {brca.get('overall_assessment', 'No high-risk variants identified')}")
            
            for gene in ['brca1', 'brca2']:
                gene_data = brca.get(gene, {})
                if gene_data.get('pathogenic_variants', 0) > 0:
                    content.append(f"- **{gene.upper()}**: {gene_data.get('risk_assessment', '')}")
        
        # APOE analysis
        apoe = disease_results.get('apoe_analysis', {})
        if apoe and apoe.get('variants_found', 0) > 0:
            content.append(f"\n### Alzheimer's Disease Risk (APOE)")
            content.append(f"**Genotype**: {apoe.get('predicted_genotype', 'Unknown')}")
            content.append(f"**Risk Level**: {apoe.get('alzheimer_risk', 'Unknown')}")
        
        # HFE analysis
        hfe = disease_results.get('hfe_analysis', {})
        if hfe and hfe.get('variants_found', 0) > 0:
            content.append(f"\n### Hemochromatosis Risk (HFE)")
            content.append(f"**Risk Assessment**: {hfe.get('hemochromatosis_risk', 'Unknown')}")
        
        content.append(f"\n*Full disease risk analysis available in separate report*")
        return content
    
    def _generate_traits_section(self, traits_results: Dict[str, Any]) -> List[str]:
        """Generate traits and ancestry section."""
        content = ["\n## Traits and Ancestry Analysis"]
        content.append("*Analysis of physical traits, nutritional genomics, and ancestry markers*")
        
        summary = traits_results.get('summary', {})
        content.append(f"\n**Traits Analyzed**: {summary.get('traits_analyzed', 0)}")
        content.append(f"**Nutritional Markers**: {summary.get('nutritional_markers', 0)}")
        
        # Nutritional genomics highlights
        nutritional = traits_results.get('nutritional_genomics', {})
        if nutritional:
            content.append(f"\n### Key Nutritional Findings")
            
            for marker, data in nutritional.items():
                if marker in ['lactose_tolerance', 'caffeine_metabolism']:
                    content.append(f"- **{marker.replace('_', ' ').title()}**: {data.get('phenotype', 'Unknown')}")
        
        # Ancestry
        ancestry = traits_results.get('ancestry_markers', {})
        if ancestry:
            content.append(f"\n### Ancestry Analysis")
            content.append(f"**Predicted Ancestry**: {ancestry.get('predicted_ancestry', 'Unknown')}")
        
        content.append(f"\n*Full traits and ancestry analysis available in separate report*")
        return content
    
    def _generate_variant_details_section(self, variant_results: Dict[str, Any]) -> List[str]:
        """Generate variant details section."""
        content = ["\n## Variant Analysis Summary"]
        content.append("*Overview of genetic variants identified in the analysis*")
        
        # This would be populated with variant statistics
        content.append(f"\n**Total Variants Analyzed**: {variant_results.get('total_variants', 'Unknown')}")
        content.append(f"**Clinically Significant Variants**: {variant_results.get('clinically_significant', 'Unknown')}")
        content.append(f"**Pharmacogenomics Variants**: {variant_results.get('pharmaco_variants', 'Unknown')}")
        
        return content
    
    def _generate_recommendations_section(self, results: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations section."""
        content = ["\n## Comprehensive Recommendations"]
        
        # Immediate actions
        high_priority_actions = []
        
        # Check for high-priority findings that require immediate action
        if 'disease_risk' in results:
            disease_summary = results['disease_risk'].get('summary', {})
            if len(disease_summary.get('high_risk_findings', [])) > 0:
                high_priority_actions.append("Consult with a genetic counselor immediately")
                high_priority_actions.append("Discuss findings with primary care physician")
        
        if 'pharmacogenomics' in results:
            pharmaco_summary = results['pharmacogenomics'].get('summary', {})
            if len(pharmaco_summary.get('high_risk_findings', [])) > 0:
                high_priority_actions.append("Review current medications with healthcare provider")
                high_priority_actions.append("Consider pharmacogenomics consultation")
        
        if high_priority_actions:
            content.append(f"\n### 🚨 Immediate Actions Required")
            for action in high_priority_actions:
                content.append(f"- **{action}**")
        
        # Healthcare consultations
        content.append(f"\n### Healthcare Consultations")
        content.append("- **Primary Care Physician**: Discuss all findings and integrate with medical history")
        content.append("- **Genetic Counselor**: Essential for interpreting high-risk findings")
        content.append("- **Clinical Pharmacist**: For medication-related findings")
        content.append("- **Specialist Referrals**: As recommended by primary care physician")
        
        # Lifestyle recommendations
        content.append(f"\n### Lifestyle Recommendations")
        content.append("- Maintain a healthy, balanced diet rich in folate and B vitamins")
        content.append("- Regular exercise and stress management")
        content.append("- Avoid smoking and limit alcohol consumption")
        content.append("- Follow personalized recommendations based on specific findings")
        
        # Monitoring and follow-up
        content.append(f"\n### Monitoring and Follow-up")
        content.append("- Regular health screenings as appropriate for age and risk factors")
        content.append("- Periodic review of genetic findings as science advances")
        content.append("- Family cascade testing for actionable findings")
        content.append("- Keep genetic information updated in medical records")
        
        return content
    
    def _generate_footer(self) -> List[str]:
        """Generate report footer."""
        return [
            "\n---",
            "\n## Report Information",
            "**Generated by**: GenomeAI Enhanced Genomics Pipeline",
            "**Analysis Modules**: Pharmacogenomics, MTHFR, Disease Risk, Traits & Ancestry",
            "**Version**: 1.0.0",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n### Data Sources and References",
            "- PharmGKB: Pharmacogenomics Knowledge Base",
            "- ClinVar: Clinical Variant Database",
            "- CPIC: Clinical Pharmacogenetics Implementation Consortium",
            "- Ensembl VEP: Variant Effect Predictor",
            "\n### Quality and Limitations",
            "- Analysis based on current scientific knowledge (subject to change)",
            "- Variant interpretation may evolve as research advances",
            "- Individual responses to genetic variants vary significantly",
            "- Environmental and lifestyle factors significantly influence outcomes",
            "\n**For Research and Educational Purposes Only**",
            "*Not for medical diagnosis or treatment decisions*"
        ]
    
    def _generate_html_report(self, content: List[str], outdir: Path) -> str:
        """Generate HTML version of the report."""
        html_content = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "<title>Comprehensive Genomics Analysis Report</title>",
            "<style>",
            "body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; line-height: 1.6; }",
            "h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }",
            "h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; margin-top: 30px; }",
            "h3 { color: #2980b9; margin-top: 25px; }",
            ".disclaimer { background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }",
            ".high-priority { background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 5px; margin: 10px 0; }",
            ".moderate-risk { background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }",
            ".actionable { background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; border-radius: 5px; margin: 10px 0; }",
            "ul { padding-left: 20px; }",
            "li { margin: 5px 0; }",
            "strong { color: #2c3e50; }",
            ".footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #ecf0f1; font-size: 0.9em; color: #7f8c8d; }",
            "</style>",
            "</head>",
            "<body>"
        ]
        
        # Convert markdown-style content to HTML
        for line in content:
            if line.startswith('# '):
                html_content.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith('## '):
                html_content.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith('### '):
                html_content.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith('**') and line.endswith('**'):
                html_content.append(f"<p><strong>{line[2:-2]}</strong></p>")
            elif 'DISCLAIMER' in line or 'CRITICAL' in line:
                html_content.append(f"<div class='disclaimer'>{line}</div>")
            elif '🚨' in line:
                html_content.append(f"<div class='high-priority'>{line}</div>")
            elif '⚠️' in line:
                html_content.append(f"<div class='moderate-risk'>{line}</div>")
            elif '💡' in line:
                html_content.append(f"<div class='actionable'>{line}</div>")
            elif line.startswith('- '):
                html_content.append(f"<li>{line[2:]}</li>")
            elif line.strip() == '---':
                html_content.append("<hr>")
            elif line.strip():
                html_content.append(f"<p>{line}</p>")
            else:
                html_content.append("<br>")
        
        html_content.extend([
            "</body>",
            "</html>"
        ])
        
        # Save HTML file
        html_file = outdir / "comprehensive_genomics_report.html"
        with open(html_file, 'w') as f:
            f.write('\n'.join(html_content))
        
        return str(html_file)


def generate_enhanced_reports(outdir: Path, config: Dict[str, Any], **module_results) -> Dict[str, str]:
    """
    Generate all enhanced reports.
    
    Args:
        outdir: Output directory
        config: Configuration dictionary
        **module_results: Results from individual analysis modules
        
    Returns:
        Dictionary of generated report paths
    """
    generator = EnhancedReportGenerator(config)
    
    reports = {}
    
    # Generate comprehensive report
    comprehensive_report = generator.generate_comprehensive_report(outdir, module_results)
    reports['comprehensive'] = comprehensive_report
    
    return reports