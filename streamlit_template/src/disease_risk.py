"""
Disease risk analysis module for common genetic risk markers.
Analyzes variants in genes like BRCA1/2, APOE, HFE, and other disease-associated genes.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DiseaseRiskAnalyzer:
    """Analyzer for disease risk variants."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize disease risk analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.disease_genes = self._get_disease_gene_info()
    
    def analyze_disease_risk(self, variants_file: str, outdir: Path) -> Dict[str, Any]:
        """
        Analyze variants for disease risk implications.
        
        Args:
            variants_file: Path to annotated variants file
            outdir: Output directory
            
        Returns:
            Dictionary of disease risk results
        """
        logger.info("Starting disease risk analysis")
        
        # Load variants
        df = self._load_variants(variants_file)
        
        # Analyze disease risk genes
        results = {
            'brca_analysis': self._analyze_brca_genes(df),
            'apoe_analysis': self._analyze_apoe(df),
            'hfe_analysis': self._analyze_hfe(df),
            'cardiovascular_risk': self._analyze_cardiovascular_genes(df),
            'cancer_predisposition': self._analyze_cancer_genes(df),
            'metabolic_disorders': self._analyze_metabolic_genes(df),
            'neurological_disorders': self._analyze_neurological_genes(df),
            'summary': {}
        }
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        # Save results
        self._save_results(results, outdir)
        
        logger.info("Disease risk analysis completed")
        return results
    
    def _load_variants(self, variants_file: str) -> pd.DataFrame:
        """Load variants from file."""
        if variants_file.endswith('.parquet'):
            return pd.read_parquet(variants_file)
        else:
            return pd.read_csv(variants_file, sep='\t')
    
    def _get_disease_gene_info(self) -> Dict[str, Any]:
        """Get disease gene information."""
        return {
            'BRCA1': {
                'chromosome': '17',
                'disease': 'Hereditary Breast and Ovarian Cancer',
                'inheritance': 'Autosomal Dominant',
                'lifetime_risk': {
                    'breast_cancer': '55-72%',
                    'ovarian_cancer': '39-44%'
                }
            },
            'BRCA2': {
                'chromosome': '13',
                'disease': 'Hereditary Breast and Ovarian Cancer',
                'inheritance': 'Autosomal Dominant',
                'lifetime_risk': {
                    'breast_cancer': '45-69%',
                    'ovarian_cancer': '11-17%'
                }
            },
            'APOE': {
                'chromosome': '19',
                'disease': 'Alzheimer Disease',
                'variants': {
                    'e2': 'Protective',
                    'e3': 'Neutral',
                    'e4': 'Risk factor'
                }
            },
            'HFE': {
                'chromosome': '6',
                'disease': 'Hereditary Hemochromatosis',
                'variants': {
                    'C282Y': 'Major risk variant',
                    'H63D': 'Minor risk variant'
                }
            }
        }
    
    def _analyze_brca_genes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze BRCA1 and BRCA2 variants."""
        brca1_variants = df[df['Gene'] == 'BRCA1'] if 'Gene' in df.columns else pd.DataFrame()
        brca2_variants = df[df['Gene'] == 'BRCA2'] if 'Gene' in df.columns else pd.DataFrame()
        
        result = {
            'brca1': {
                'variants_found': len(brca1_variants),
                'pathogenic_variants': 0,
                'risk_assessment': 'Population risk',
                'recommendations': []
            },
            'brca2': {
                'variants_found': len(brca2_variants),
                'pathogenic_variants': 0,
                'risk_assessment': 'Population risk',
                'recommendations': []
            },
            'overall_assessment': 'No high-risk BRCA variants identified'
        }
        
        # Analyze BRCA1 variants
        if not brca1_variants.empty:
            pathogenic_count = 0
            for _, variant in brca1_variants.iterrows():
                clin_sig = variant.get('Clinical_Significance', '').lower()
                if 'pathogenic' in clin_sig and 'likely' not in clin_sig:
                    pathogenic_count += 1
            
            result['brca1']['pathogenic_variants'] = pathogenic_count
            if pathogenic_count > 0:
                result['brca1']['risk_assessment'] = 'High risk for hereditary breast/ovarian cancer'
                result['brca1']['recommendations'] = [
                    'Genetic counseling strongly recommended',
                    'Enhanced breast cancer screening (MRI + mammography)',
                    'Consider risk-reducing strategies',
                    'Family cascade testing recommended'
                ]
        
        # Analyze BRCA2 variants
        if not brca2_variants.empty:
            pathogenic_count = 0
            for _, variant in brca2_variants.iterrows():
                clin_sig = variant.get('Clinical_Significance', '').lower()
                if 'pathogenic' in clin_sig and 'likely' not in clin_sig:
                    pathogenic_count += 1
            
            result['brca2']['pathogenic_variants'] = pathogenic_count
            if pathogenic_count > 0:
                result['brca2']['risk_assessment'] = 'High risk for hereditary breast/ovarian cancer'
                result['brca2']['recommendations'] = [
                    'Genetic counseling strongly recommended',
                    'Enhanced breast cancer screening',
                    'Consider risk-reducing strategies',
                    'Family cascade testing recommended'
                ]
        
        # Overall assessment
        if result['brca1']['pathogenic_variants'] > 0 or result['brca2']['pathogenic_variants'] > 0:
            result['overall_assessment'] = 'High-risk BRCA variant(s) identified - immediate genetic counseling recommended'
        
        return result
    
    def _analyze_apoe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze APOE variants for Alzheimer's disease risk."""
        apoe_variants = df[df['Gene'] == 'APOE'] if 'Gene' in df.columns else pd.DataFrame()
        
        result = {
            'variants_found': len(apoe_variants),
            'predicted_genotype': 'e3/e3',
            'alzheimer_risk': 'Average population risk',
            'risk_multiplier': '1x',
            'recommendations': []
        }
        
        # Mock APOE genotype determination (would require specific variant analysis)
        if not apoe_variants.empty:
            # Simplified analysis - would need specific rs429358 and rs7412 analysis
            high_risk_variants = 0
            for _, variant in apoe_variants.iterrows():
                # Check for known APOE risk variants
                dbsnp_id = variant.get('dbSNP_ID', '')
                if 'rs429358' in str(dbsnp_id):  # APOE e4 marker
                    high_risk_variants += 1
            
            if high_risk_variants >= 2:
                result['predicted_genotype'] = 'e4/e4'
                result['alzheimer_risk'] = 'Significantly increased risk'
                result['risk_multiplier'] = '8-12x'
                result['recommendations'] = [
                    'Lifestyle interventions for brain health',
                    'Regular cognitive assessments',
                    'Cardiovascular risk reduction',
                    'Consider genetic counseling'
                ]
            elif high_risk_variants == 1:
                result['predicted_genotype'] = 'e3/e4'
                result['alzheimer_risk'] = 'Moderately increased risk'
                result['risk_multiplier'] = '3-4x'
                result['recommendations'] = [
                    'Lifestyle interventions for brain health',
                    'Regular exercise and cognitive stimulation',
                    'Heart-healthy diet (Mediterranean diet)'
                ]
        
        return result
    
    def _analyze_hfe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze HFE variants for hemochromatosis risk."""
        hfe_variants = df[df['Gene'] == 'HFE'] if 'Gene' in df.columns else pd.DataFrame()
        
        result = {
            'variants_found': len(hfe_variants),
            'c282y_status': 'Wild-type',
            'h63d_status': 'Wild-type',
            'hemochromatosis_risk': 'Low risk',
            'recommendations': []
        }
        
        if not hfe_variants.empty:
            c282y_count = 0
            h63d_count = 0
            
            for _, variant in hfe_variants.iterrows():
                # Check for specific HFE variants
                amino_acid = variant.get('Amino_acids', '')
                if 'C/Y' in str(amino_acid):  # C282Y
                    c282y_count += 1
                elif 'H/D' in str(amino_acid):  # H63D
                    h63d_count += 1
            
            # Update status based on variants found
            if c282y_count == 2:
                result['c282y_status'] = 'Homozygous (C282Y/C282Y)'
                result['hemochromatosis_risk'] = 'High risk'
                result['recommendations'] = [
                    'Iron studies (ferritin, transferrin saturation)',
                    'Regular monitoring for iron overload',
                    'Genetic counseling',
                    'Family screening recommended'
                ]
            elif c282y_count == 1:
                result['c282y_status'] = 'Heterozygous (C282Y/+)'
                result['hemochromatosis_risk'] = 'Carrier - low personal risk'
                result['recommendations'] = [
                    'Baseline iron studies',
                    'Family screening may be indicated'
                ]
            
            if h63d_count >= 1:
                result['h63d_status'] = f"{'Homozygous' if h63d_count == 2 else 'Heterozygous'} H63D"
                if c282y_count == 1 and h63d_count >= 1:
                    result['hemochromatosis_risk'] = 'Moderate risk (compound heterozygote)'
        
        return result
    
    def _analyze_cardiovascular_genes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze cardiovascular disease risk genes."""
        cardio_genes = ['LDLR', 'PCSK9', 'APOB', 'MYBPC3', 'MYH7', 'TNNT2', 'TNNI3']
        
        results = {}
        for gene in cardio_genes:
            gene_variants = df[df['Gene'] == gene] if 'Gene' in df.columns else pd.DataFrame()
            
            if not gene_variants.empty:
                pathogenic_variants = 0
                for _, variant in gene_variants.iterrows():
                    clin_sig = variant.get('Clinical_Significance', '').lower()
                    if 'pathogenic' in clin_sig:
                        pathogenic_variants += 1
                
                results[gene] = {
                    'variants_found': len(gene_variants),
                    'pathogenic_variants': pathogenic_variants,
                    'risk_assessment': 'Increased cardiovascular risk' if pathogenic_variants > 0 else 'No significant risk variants'
                }
        
        return results
    
    def _analyze_cancer_genes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze cancer predisposition genes."""
        cancer_genes = ['TP53', 'APC', 'MLH1', 'MSH2', 'MSH6', 'PMS2', 'PALB2', 'ATM', 'CHEK2']
        
        results = {}
        for gene in cancer_genes:
            gene_variants = df[df['Gene'] == gene] if 'Gene' in df.columns else pd.DataFrame()
            
            if not gene_variants.empty:
                pathogenic_variants = 0
                for _, variant in gene_variants.iterrows():
                    clin_sig = variant.get('Clinical_Significance', '').lower()
                    if 'pathogenic' in clin_sig:
                        pathogenic_variants += 1
                
                if pathogenic_variants > 0:
                    results[gene] = {
                        'variants_found': len(gene_variants),
                        'pathogenic_variants': pathogenic_variants,
                        'cancer_syndrome': self._get_cancer_syndrome(gene),
                        'recommendations': self._get_cancer_screening_recommendations(gene)
                    }
        
        return results
    
    def _analyze_metabolic_genes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze metabolic disorder genes."""
        metabolic_genes = ['PAH', 'CFTR', 'GBA', 'HEXA', 'SMN1']
        
        results = {}
        for gene in metabolic_genes:
            gene_variants = df[df['Gene'] == gene] if 'Gene' in df.columns else pd.DataFrame()
            
            if not gene_variants.empty:
                results[gene] = {
                    'variants_found': len(gene_variants),
                    'disorder': self._get_metabolic_disorder(gene),
                    'inheritance': 'Autosomal Recessive',
                    'carrier_status': 'Possible carrier' if len(gene_variants) > 0 else 'Unlikely carrier'
                }
        
        return results
    
    def _analyze_neurological_genes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze neurological disorder genes."""
        neuro_genes = ['HTT', 'SNCA', 'LRRK2', 'PARK7', 'PINK1', 'PRKN']
        
        results = {}
        for gene in neuro_genes:
            gene_variants = df[df['Gene'] == gene] if 'Gene' in df.columns else pd.DataFrame()
            
            if not gene_variants.empty:
                results[gene] = {
                    'variants_found': len(gene_variants),
                    'disorder': self._get_neurological_disorder(gene),
                    'risk_assessment': 'Requires clinical correlation'
                }
        
        return results
    
    def _get_cancer_syndrome(self, gene: str) -> str:
        """Get cancer syndrome associated with gene."""
        syndromes = {
            'TP53': 'Li-Fraumeni syndrome',
            'APC': 'Familial adenomatous polyposis',
            'MLH1': 'Lynch syndrome',
            'MSH2': 'Lynch syndrome',
            'MSH6': 'Lynch syndrome',
            'PMS2': 'Lynch syndrome',
            'PALB2': 'Hereditary breast cancer',
            'ATM': 'Ataxia-telangiectasia',
            'CHEK2': 'Hereditary breast cancer'
        }
        return syndromes.get(gene, 'Unknown syndrome')
    
    def _get_cancer_screening_recommendations(self, gene: str) -> List[str]:
        """Get cancer screening recommendations for gene."""
        recommendations = {
            'TP53': [
                'Annual whole-body MRI screening',
                'Enhanced cancer surveillance protocol',
                'Genetic counseling essential'
            ],
            'APC': [
                'Colonoscopy starting age 10-15',
                'Annual screening recommended',
                'Consider prophylactic colectomy'
            ],
            'MLH1': [
                'Colonoscopy every 1-2 years starting age 20-25',
                'Endometrial cancer screening for women',
                'Consider other Lynch-associated cancers'
            ]
        }
        return recommendations.get(gene, ['Genetic counseling recommended'])
    
    def _get_metabolic_disorder(self, gene: str) -> str:
        """Get metabolic disorder associated with gene."""
        disorders = {
            'PAH': 'Phenylketonuria',
            'CFTR': 'Cystic fibrosis',
            'GBA': 'Gaucher disease',
            'HEXA': 'Tay-Sachs disease',
            'SMN1': 'Spinal muscular atrophy'
        }
        return disorders.get(gene, 'Unknown disorder')
    
    def _get_neurological_disorder(self, gene: str) -> str:
        """Get neurological disorder associated with gene."""
        disorders = {
            'HTT': 'Huntington disease',
            'SNCA': 'Parkinson disease',
            'LRRK2': 'Parkinson disease',
            'PARK7': 'Parkinson disease',
            'PINK1': 'Parkinson disease',
            'PRKN': 'Parkinson disease'
        }
        return disorders.get(gene, 'Unknown disorder')
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of disease risk results."""
        summary = {
            'high_risk_findings': [],
            'moderate_risk_findings': [],
            'carrier_status': [],
            'total_genes_analyzed': 0,
            'genes_with_variants': 0,
            'actionable_findings': 0
        }
        
        # Analyze BRCA results
        brca = results.get('brca_analysis', {})
        if brca.get('brca1', {}).get('pathogenic_variants', 0) > 0:
            summary['high_risk_findings'].append('BRCA1 pathogenic variant')
            summary['actionable_findings'] += 1
        if brca.get('brca2', {}).get('pathogenic_variants', 0) > 0:
            summary['high_risk_findings'].append('BRCA2 pathogenic variant')
            summary['actionable_findings'] += 1
        
        # Analyze APOE results
        apoe = results.get('apoe_analysis', {})
        if 'e4' in apoe.get('predicted_genotype', ''):
            if apoe.get('predicted_genotype') == 'e4/e4':
                summary['high_risk_findings'].append('APOE e4/e4 - high Alzheimer risk')
            else:
                summary['moderate_risk_findings'].append('APOE e4 carrier - increased Alzheimer risk')
        
        # Count other findings
        for category in ['cardiovascular_risk', 'cancer_predisposition', 'metabolic_disorders']:
            category_results = results.get(category, {})
            for gene, data in category_results.items():
                summary['total_genes_analyzed'] += 1
                if isinstance(data, dict) and data.get('variants_found', 0) > 0:
                    summary['genes_with_variants'] += 1
                    
                    if data.get('pathogenic_variants', 0) > 0:
                        summary['actionable_findings'] += 1
        
        return summary
    
    def _save_results(self, results: Dict[str, Any], outdir: Path) -> None:
        """Save disease risk results."""
        disease_dir = outdir / "disease_risk"
        disease_dir.mkdir(exist_ok=True)
        
        # Save JSON results
        json_file = disease_dir / "disease_risk_results.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Disease risk results saved to {disease_dir}")


def analyze_disease_risk_variants(variants_file: str, outdir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to analyze disease risk variants.
    
    Args:
        variants_file: Path to annotated variants file
        outdir: Output directory
        config: Configuration dictionary
        
    Returns:
        Disease risk analysis results
    """
    analyzer = DiseaseRiskAnalyzer(config)
    return analyzer.analyze_disease_risk(variants_file, outdir)


def generate_disease_risk_report(results: Dict[str, Any], outdir: Path) -> str:
    """Generate disease risk analysis report."""
    report_content = []
    
    # Header
    report_content.append("# Disease Risk Analysis Report")
    report_content.append("\n**CRITICAL MEDICAL DISCLAIMER**: This analysis is for research purposes only and should NOT be used for medical diagnosis or clinical decision-making. Genetic counseling and clinical correlation are essential for proper interpretation of these results. Always consult qualified healthcare providers.")
    
    # Summary
    summary = results.get('summary', {})
    report_content.append("\n## Executive Summary")
    report_content.append(f"- **High-Risk Findings**: {len(summary.get('high_risk_findings', []))}")
    report_content.append(f"- **Moderate-Risk Findings**: {len(summary.get('moderate_risk_findings', []))}")
    report_content.append(f"- **Actionable Findings**: {summary.get('actionable_findings', 0)}")
    report_content.append(f"- **Genes Analyzed**: {summary.get('total_genes_analyzed', 0)}")
    
    # High-priority findings
    high_risk = summary.get('high_risk_findings', [])
    if high_risk:
        report_content.append("\n### 🚨 High-Priority Findings Requiring Immediate Attention")
        for finding in high_risk:
            report_content.append(f"- **{finding}** - Genetic counseling strongly recommended")
    
    # BRCA Analysis
    brca = results.get('brca_analysis', {})
    if brca:
        report_content.append("\n## Hereditary Cancer Risk (BRCA1/BRCA2)")
        report_content.append(f"**Overall Assessment**: {brca.get('overall_assessment', 'Unknown')}")
        
        for gene in ['brca1', 'brca2']:
            gene_data = brca.get(gene, {})
            if gene_data.get('variants_found', 0) > 0:
                report_content.append(f"\n### {gene.upper()}")
                report_content.append(f"**Variants Found**: {gene_data.get('variants_found', 0)}")
                report_content.append(f"**Pathogenic Variants**: {gene_data.get('pathogenic_variants', 0)}")
                report_content.append(f"**Risk Assessment**: {gene_data.get('risk_assessment', 'Unknown')}")
                
                recommendations = gene_data.get('recommendations', [])
                if recommendations:
                    report_content.append("**Recommendations**:")
                    for rec in recommendations:
                        report_content.append(f"- {rec}")
    
    # APOE Analysis
    apoe = results.get('apoe_analysis', {})
    if apoe and apoe.get('variants_found', 0) > 0:
        report_content.append("\n## Alzheimer's Disease Risk (APOE)")
        report_content.append(f"**Predicted Genotype**: {apoe.get('predicted_genotype', 'Unknown')}")
        report_content.append(f"**Alzheimer's Risk**: {apoe.get('alzheimer_risk', 'Unknown')}")
        report_content.append(f"**Risk Multiplier**: {apoe.get('risk_multiplier', 'Unknown')}")
        
        recommendations = apoe.get('recommendations', [])
        if recommendations:
            report_content.append("**Recommendations**:")
            for rec in recommendations:
                report_content.append(f"- {rec}")
    
    # HFE Analysis
    hfe = results.get('hfe_analysis', {})
    if hfe and hfe.get('variants_found', 0) > 0:
        report_content.append("\n## Hereditary Hemochromatosis Risk (HFE)")
        report_content.append(f"**C282Y Status**: {hfe.get('c282y_status', 'Unknown')}")
        report_content.append(f"**H63D Status**: {hfe.get('h63d_status', 'Unknown')}")
        report_content.append(f"**Hemochromatosis Risk**: {hfe.get('hemochromatosis_risk', 'Unknown')}")
        
        recommendations = hfe.get('recommendations', [])
        if recommendations:
            report_content.append("**Recommendations**:")
            for rec in recommendations:
                report_content.append(f"- {rec}")
    
    # Cancer Predisposition
    cancer = results.get('cancer_predisposition', {})
    if cancer:
        report_content.append("\n## Cancer Predisposition Genes")
        for gene, data in cancer.items():
            report_content.append(f"\n### {gene}")
            report_content.append(f"**Cancer Syndrome**: {data.get('cancer_syndrome', 'Unknown')}")
            report_content.append(f"**Pathogenic Variants**: {data.get('pathogenic_variants', 0)}")
            
            recommendations = data.get('recommendations', [])
            if recommendations:
                report_content.append("**Screening Recommendations**:")
                for rec in recommendations:
                    report_content.append(f"- {rec}")
    
    # Carrier Status
    metabolic = results.get('metabolic_disorders', {})
    if metabolic:
        report_content.append("\n## Carrier Status (Recessive Disorders)")
        for gene, data in metabolic.items():
            report_content.append(f"- **{gene}** ({data.get('disorder', 'Unknown')}): {data.get('carrier_status', 'Unknown')}")
    
    # Important Notes
    report_content.append("\n## Important Considerations")
    report_content.append("- Genetic variants are only one factor in disease risk")
    report_content.append("- Environmental factors, lifestyle, and family history also contribute significantly")
    report_content.append("- Penetrance (likelihood of developing disease) varies widely")
    report_content.append("- Regular medical care and screening remain important regardless of genetic status")
    
    # Next Steps
    report_content.append("\n## Recommended Next Steps")
    if summary.get('actionable_findings', 0) > 0:
        report_content.append("1. **Immediate**: Consult with a genetic counselor")
        report_content.append("2. **Follow-up**: Discuss results with primary care physician")
        report_content.append("3. **Family**: Consider cascade testing for at-risk family members")
        report_content.append("4. **Screening**: Implement appropriate screening protocols")
    else:
        report_content.append("1. Continue routine medical care and screening")
        report_content.append("2. Maintain healthy lifestyle practices")
        report_content.append("3. Stay informed about family medical history")
    
    report_content.append(f"\n---\n*Report generated by GenomeAI Disease Risk Analysis Module*")
    
    # Save report
    report_file = outdir / "disease_risk" / "disease_risk_report.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_content))
    
    logger.info(f"Disease risk report saved to {report_file}")
    return str(report_file)