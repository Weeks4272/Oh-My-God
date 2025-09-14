"""
Pharmacogenomics module for drug-gene interaction analysis.
Integrates PharmGKB and CPIC guidelines for drug metabolism predictions.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class PharmacogenomicsAnalyzer:
    """Analyzer for pharmacogenomics variants and drug interactions."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize pharmacogenomics analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.pharmgkb_data = self._load_pharmgkb_data()
        self.cpic_guidelines = self._load_cpic_guidelines()
        
    def analyze_variants(self, variants_file: str, outdir: Path) -> Dict[str, Any]:
        """
        Analyze variants for pharmacogenomics implications.
        
        Args:
            variants_file: Path to annotated variants file
            outdir: Output directory
            
        Returns:
            Dictionary of pharmacogenomics results
        """
        logger.info("Starting pharmacogenomics analysis")
        
        # Load variants
        df = self._load_variants(variants_file)
        
        # Analyze key pharmacogenes
        pharmaco_results = {
            'cyp2d6': self._analyze_cyp2d6(df),
            'cyp2c19': self._analyze_cyp2c19(df),
            'cyp3a4': self._analyze_cyp3a4(df),
            'tpmt': self._analyze_tpmt(df),
            'dpyd': self._analyze_dpyd(df),
            'slco1b1': self._analyze_slco1b1(df),
            'ugt1a1': self._analyze_ugt1a1(df),
            'vkorc1': self._analyze_vkorc1(df),
            'summary': {}
        }
        
        # Generate summary
        pharmaco_results['summary'] = self._generate_summary(pharmaco_results)
        
        # Save results
        self._save_results(pharmaco_results, outdir)
        
        logger.info("Pharmacogenomics analysis completed")
        return pharmaco_results
    
    def _load_variants(self, variants_file: str) -> pd.DataFrame:
        """Load variants from file."""
        if variants_file.endswith('.parquet'):
            return pd.read_parquet(variants_file)
        else:
            return pd.read_csv(variants_file, sep='\t')
    
    def _load_pharmgkb_data(self) -> Dict[str, Any]:
        """Load PharmGKB data or create mock data."""
        pharmgkb_config = self.config.get('pharmacogenomics', {}).get('pharmgkb', {})
        data_file = pharmgkb_config.get('data_file')
        
        if data_file and Path(data_file).exists():
            with open(data_file, 'r') as f:
                return json.load(f)
        
        # Mock PharmGKB data
        return {
            'CYP2D6': {
                'variants': {
                    'rs16947': {'allele': '*2', 'function': 'normal'},
                    'rs3892097': {'allele': '*4', 'function': 'no_function'},
                    'rs5030655': {'allele': '*6', 'function': 'no_function'},
                    'rs28371706': {'allele': '*41', 'function': 'decreased'}
                },
                'drugs': ['codeine', 'tramadol', 'metoprolol', 'paroxetine']
            },
            'CYP2C19': {
                'variants': {
                    'rs4244285': {'allele': '*2', 'function': 'no_function'},
                    'rs4986893': {'allele': '*3', 'function': 'no_function'},
                    'rs12248560': {'allele': '*17', 'function': 'increased'}
                },
                'drugs': ['clopidogrel', 'omeprazole', 'escitalopram']
            },
            'TPMT': {
                'variants': {
                    'rs1800462': {'allele': '*2', 'function': 'decreased'},
                    'rs1800460': {'allele': '*3A', 'function': 'decreased'},
                    'rs1142345': {'allele': '*3C', 'function': 'decreased'}
                },
                'drugs': ['azathioprine', 'mercaptopurine', 'thioguanine']
            }
        }
    
    def _load_cpic_guidelines(self) -> Dict[str, Any]:
        """Load CPIC guidelines or create mock data."""
        return {
            'CYP2D6': {
                'metabolizer_phenotypes': {
                    'poor': 'Activity Score 0',
                    'intermediate': 'Activity Score 0.25-1.0',
                    'normal': 'Activity Score 1.25-2.25',
                    'ultrarapid': 'Activity Score >2.25'
                },
                'recommendations': {
                    'codeine': {
                        'poor': 'Avoid codeine use. Consider alternative analgesics.',
                        'intermediate': 'Use label-recommended age- or weight-specific dosing.',
                        'normal': 'Use label-recommended age- or weight-specific dosing.',
                        'ultrarapid': 'Avoid codeine use due to potential for toxicity.'
                    }
                }
            },
            'CYP2C19': {
                'metabolizer_phenotypes': {
                    'poor': 'Two no-function alleles',
                    'intermediate': 'One no-function allele',
                    'normal': 'Two normal function alleles',
                    'rapid': 'One increased function allele',
                    'ultrarapid': 'Two increased function alleles'
                },
                'recommendations': {
                    'clopidogrel': {
                        'poor': 'Alternative antiplatelet therapy recommended.',
                        'intermediate': 'Alternative antiplatelet therapy recommended.',
                        'normal': 'Standard dosing and monitoring.',
                        'rapid': 'Standard dosing and monitoring.',
                        'ultrarapid': 'Standard dosing and monitoring.'
                    }
                }
            }
        }
    
    def _analyze_cyp2d6(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze CYP2D6 variants."""
        cyp2d6_variants = df[df['Gene'] == 'CYP2D6'] if 'Gene' in df.columns else pd.DataFrame()
        
        result = {
            'gene': 'CYP2D6',
            'variants_found': [],
            'predicted_phenotype': 'normal',
            'activity_score': 2.0,
            'drug_recommendations': {},
            'clinical_significance': 'Normal metabolizer for CYP2D6 substrates'
        }
        
        if not cyp2d6_variants.empty:
            for _, variant in cyp2d6_variants.iterrows():
                variant_info = {
                    'position': variant.get('Genomic_Position', ''),
                    'consequence': variant.get('Consequence', ''),
                    'dbsnp_id': variant.get('dbSNP_ID', ''),
                    'allele_function': 'normal'  # Would be determined from PharmGKB data
                }
                result['variants_found'].append(variant_info)
        
        # Mock phenotype prediction
        if len(result['variants_found']) == 0:
            result['predicted_phenotype'] = 'normal'
            result['activity_score'] = 2.0
        elif len(result['variants_found']) == 1:
            result['predicted_phenotype'] = 'intermediate'
            result['activity_score'] = 1.0
        else:
            result['predicted_phenotype'] = 'poor'
            result['activity_score'] = 0.0
        
        # Add drug recommendations
        result['drug_recommendations'] = self._get_drug_recommendations('CYP2D6', result['predicted_phenotype'])
        
        return result
    
    def _analyze_cyp2c19(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze CYP2C19 variants."""
        cyp2c19_variants = df[df['Gene'] == 'CYP2C19'] if 'Gene' in df.columns else pd.DataFrame()
        
        result = {
            'gene': 'CYP2C19',
            'variants_found': [],
            'predicted_phenotype': 'normal',
            'drug_recommendations': {},
            'clinical_significance': 'Normal metabolizer for CYP2C19 substrates'
        }
        
        if not cyp2c19_variants.empty:
            for _, variant in cyp2c19_variants.iterrows():
                variant_info = {
                    'position': variant.get('Genomic_Position', ''),
                    'consequence': variant.get('Consequence', ''),
                    'dbsnp_id': variant.get('dbSNP_ID', ''),
                    'allele_function': 'normal'
                }
                result['variants_found'].append(variant_info)
        
        # Predict phenotype based on variants
        if len(result['variants_found']) >= 2:
            result['predicted_phenotype'] = 'poor'
            result['clinical_significance'] = 'Poor metabolizer - reduced enzyme activity'
        elif len(result['variants_found']) == 1:
            result['predicted_phenotype'] = 'intermediate'
            result['clinical_significance'] = 'Intermediate metabolizer - reduced enzyme activity'
        
        result['drug_recommendations'] = self._get_drug_recommendations('CYP2C19', result['predicted_phenotype'])
        
        return result
    
    def _analyze_cyp3a4(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze CYP3A4 variants."""
        cyp3a4_variants = df[df['Gene'] == 'CYP3A4'] if 'Gene' in df.columns else pd.DataFrame()
        
        return {
            'gene': 'CYP3A4',
            'variants_found': len(cyp3a4_variants),
            'predicted_phenotype': 'normal',
            'clinical_significance': 'CYP3A4 is highly variable and influenced by many factors',
            'note': 'CYP3A4 phenotype prediction requires comprehensive analysis of multiple variants'
        }
    
    def _analyze_tpmt(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze TPMT variants."""
        tpmt_variants = df[df['Gene'] == 'TPMT'] if 'Gene' in df.columns else pd.DataFrame()
        
        result = {
            'gene': 'TPMT',
            'variants_found': [],
            'predicted_phenotype': 'normal',
            'drug_recommendations': {},
            'clinical_significance': 'Normal TPMT activity'
        }
        
        if not tpmt_variants.empty:
            for _, variant in tpmt_variants.iterrows():
                variant_info = {
                    'position': variant.get('Genomic_Position', ''),
                    'consequence': variant.get('Consequence', ''),
                    'dbsnp_id': variant.get('dbSNP_ID', ''),
                    'allele': 'unknown'
                }
                result['variants_found'].append(variant_info)
            
            # Predict phenotype
            if len(result['variants_found']) >= 2:
                result['predicted_phenotype'] = 'poor'
                result['clinical_significance'] = 'Poor TPMT activity - high risk of toxicity'
            elif len(result['variants_found']) == 1:
                result['predicted_phenotype'] = 'intermediate'
                result['clinical_significance'] = 'Intermediate TPMT activity - moderate risk'
        
        result['drug_recommendations'] = {
            'azathioprine': self._get_tpmt_recommendation(result['predicted_phenotype']),
            'mercaptopurine': self._get_tpmt_recommendation(result['predicted_phenotype']),
            'thioguanine': self._get_tpmt_recommendation(result['predicted_phenotype'])
        }
        
        return result
    
    def _analyze_dpyd(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze DPYD variants."""
        dpyd_variants = df[df['Gene'] == 'DPYD'] if 'Gene' in df.columns else pd.DataFrame()
        
        result = {
            'gene': 'DPYD',
            'variants_found': len(dpyd_variants),
            'predicted_phenotype': 'normal',
            'clinical_significance': 'Normal DPD activity',
            'drug_recommendations': {
                '5-fluorouracil': 'Standard dosing appropriate',
                'capecitabine': 'Standard dosing appropriate'
            }
        }
        
        if not dpyd_variants.empty:
            result['predicted_phenotype'] = 'intermediate'
            result['clinical_significance'] = 'Reduced DPD activity - increased toxicity risk'
            result['drug_recommendations'] = {
                '5-fluorouracil': 'Reduce starting dose by 50% and monitor closely',
                'capecitabine': 'Reduce starting dose by 50% and monitor closely'
            }
        
        return result
    
    def _analyze_slco1b1(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze SLCO1B1 variants."""
        slco1b1_variants = df[df['Gene'] == 'SLCO1B1'] if 'Gene' in df.columns else pd.DataFrame()
        
        result = {
            'gene': 'SLCO1B1',
            'variants_found': len(slco1b1_variants),
            'predicted_function': 'normal',
            'clinical_significance': 'Normal OATP1B1 function',
            'drug_recommendations': {
                'simvastatin': 'Standard dosing appropriate'
            }
        }
        
        if not slco1b1_variants.empty:
            result['predicted_function'] = 'decreased'
            result['clinical_significance'] = 'Decreased OATP1B1 function - increased statin exposure'
            result['drug_recommendations'] = {
                'simvastatin': 'Consider lower dose or alternative statin'
            }
        
        return result
    
    def _analyze_ugt1a1(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze UGT1A1 variants."""
        ugt1a1_variants = df[df['Gene'] == 'UGT1A1'] if 'Gene' in df.columns else pd.DataFrame()
        
        return {
            'gene': 'UGT1A1',
            'variants_found': len(ugt1a1_variants),
            'predicted_phenotype': 'normal' if ugt1a1_variants.empty else 'intermediate',
            'clinical_significance': 'UGT1A1 variants affect irinotecan metabolism',
            'drug_recommendations': {
                'irinotecan': 'Consider dose reduction if UGT1A1*28 present'
            }
        }
    
    def _analyze_vkorc1(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze VKORC1 variants."""
        vkorc1_variants = df[df['Gene'] == 'VKORC1'] if 'Gene' in df.columns else pd.DataFrame()
        
        return {
            'gene': 'VKORC1',
            'variants_found': len(vkorc1_variants),
            'predicted_sensitivity': 'normal' if vkorc1_variants.empty else 'increased',
            'clinical_significance': 'VKORC1 variants affect warfarin sensitivity',
            'drug_recommendations': {
                'warfarin': 'Consider lower starting dose if sensitive haplotype present'
            }
        }
    
    def _get_drug_recommendations(self, gene: str, phenotype: str) -> Dict[str, str]:
        """Get drug recommendations for gene/phenotype combination."""
        cpic_data = self.cpic_guidelines.get(gene, {})
        recommendations = cpic_data.get('recommendations', {})
        
        result = {}
        for drug, drug_recs in recommendations.items():
            result[drug] = drug_recs.get(phenotype, 'No specific recommendation available')
        
        return result
    
    def _get_tpmt_recommendation(self, phenotype: str) -> str:
        """Get TPMT-specific drug recommendations."""
        recommendations = {
            'normal': 'Standard dosing and monitoring appropriate',
            'intermediate': 'Consider 30-70% of standard dose with increased monitoring',
            'poor': 'Consider alternative therapy or reduce dose by 90% with intensive monitoring'
        }
        return recommendations.get(phenotype, 'Consult pharmacogenomics specialist')
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of pharmacogenomics results."""
        summary = {
            'total_genes_analyzed': 0,
            'genes_with_variants': 0,
            'high_risk_findings': [],
            'moderate_risk_findings': [],
            'drug_interactions_identified': 0,
            'recommendations_count': 0
        }
        
        for gene, data in results.items():
            if gene == 'summary':
                continue
                
            summary['total_genes_analyzed'] += 1
            
            if isinstance(data, dict):
                variants_found = data.get('variants_found', [])
                if variants_found and len(variants_found) > 0:
                    summary['genes_with_variants'] += 1
                
                phenotype = data.get('predicted_phenotype', '')
                if phenotype in ['poor', 'ultrarapid']:
                    summary['high_risk_findings'].append(f"{gene}: {phenotype} metabolizer")
                elif phenotype in ['intermediate', 'decreased']:
                    summary['moderate_risk_findings'].append(f"{gene}: {phenotype} function")
                
                drug_recs = data.get('drug_recommendations', {})
                summary['drug_interactions_identified'] += len(drug_recs)
                summary['recommendations_count'] += len(drug_recs)
        
        return summary
    
    def _save_results(self, results: Dict[str, Any], outdir: Path) -> None:
        """Save pharmacogenomics results."""
        pharmaco_dir = outdir / "pharmacogenomics"
        pharmaco_dir.mkdir(exist_ok=True)
        
        # Save JSON results
        json_file = pharmaco_dir / "pharmacogenomics_results.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save TSV summary
        summary_data = []
        for gene, data in results.items():
            if gene == 'summary' or not isinstance(data, dict):
                continue
            
            row = {
                'Gene': gene.upper(),
                'Variants_Found': len(data.get('variants_found', [])),
                'Predicted_Phenotype': data.get('predicted_phenotype', 'normal'),
                'Clinical_Significance': data.get('clinical_significance', ''),
                'Drug_Count': len(data.get('drug_recommendations', {}))
            }
            summary_data.append(row)
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            tsv_file = pharmaco_dir / "pharmacogenomics_summary.tsv"
            df.to_csv(tsv_file, sep='\t', index=False)
        
        logger.info(f"Pharmacogenomics results saved to {pharmaco_dir}")


def analyze_pharmacogenomics(variants_file: str, outdir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to analyze pharmacogenomics variants.
    
    Args:
        variants_file: Path to annotated variants file
        outdir: Output directory
        config: Configuration dictionary
        
    Returns:
        Pharmacogenomics analysis results
    """
    analyzer = PharmacogenomicsAnalyzer(config)
    return analyzer.analyze_variants(variants_file, outdir)


def generate_pharmacogenomics_report(results: Dict[str, Any], outdir: Path) -> str:
    """Generate pharmacogenomics report."""
    report_content = []
    
    # Header
    report_content.append("# Pharmacogenomics Analysis Report")
    report_content.append("\n**IMPORTANT DISCLAIMER**: This analysis is for research purposes only and should not be used for medical diagnosis or treatment decisions. Always consult with a qualified healthcare provider and clinical pharmacist before making any medication changes based on genetic information.")
    
    # Summary
    summary = results.get('summary', {})
    report_content.append("\n## Executive Summary")
    report_content.append(f"- **Genes Analyzed**: {summary.get('total_genes_analyzed', 0)}")
    report_content.append(f"- **Genes with Variants**: {summary.get('genes_with_variants', 0)}")
    report_content.append(f"- **High-Risk Findings**: {len(summary.get('high_risk_findings', []))}")
    report_content.append(f"- **Drug Interactions Identified**: {summary.get('drug_interactions_identified', 0)}")
    
    # High-risk findings
    high_risk = summary.get('high_risk_findings', [])
    if high_risk:
        report_content.append("\n### ⚠️ High-Priority Findings")
        for finding in high_risk:
            report_content.append(f"- {finding}")
    
    # Gene-specific results
    report_content.append("\n## Detailed Gene Analysis")
    
    gene_order = ['cyp2d6', 'cyp2c19', 'cyp3a4', 'tpmt', 'dpyd', 'slco1b1', 'ugt1a1', 'vkorc1']
    
    for gene in gene_order:
        if gene in results and gene != 'summary':
            data = results[gene]
            if isinstance(data, dict):
                report_content.append(f"\n### {data.get('gene', gene).upper()}")
                report_content.append(f"**Predicted Phenotype**: {data.get('predicted_phenotype', 'normal')}")
                report_content.append(f"**Clinical Significance**: {data.get('clinical_significance', '')}")
                
                variants = data.get('variants_found', [])
                if variants:
                    report_content.append(f"**Variants Found**: {len(variants)}")
                else:
                    report_content.append("**Variants Found**: None (wild-type assumed)")
                
                # Drug recommendations
                drug_recs = data.get('drug_recommendations', {})
                if drug_recs:
                    report_content.append("\n**Drug Recommendations**:")
                    for drug, recommendation in drug_recs.items():
                        report_content.append(f"- **{drug.title()}**: {recommendation}")
    
    # Footer
    report_content.append("\n## Important Notes")
    report_content.append("- Pharmacogenomics is one factor among many that influence drug response")
    report_content.append("- Environmental factors, other medications, and health conditions also affect drug metabolism")
    report_content.append("- This analysis is based on current scientific knowledge and may change as research advances")
    report_content.append("- Always consult healthcare providers before making medication decisions")
    
    report_content.append(f"\n---\n*Report generated by GenomeAI Pharmacogenomics Module*")
    
    # Save report
    report_file = outdir / "pharmacogenomics" / "pharmacogenomics_report.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_content))
    
    logger.info(f"Pharmacogenomics report saved to {report_file}")
    return str(report_file)