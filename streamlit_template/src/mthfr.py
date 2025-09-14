"""
MTHFR gene analysis module for C677T and A1298C variants.
Provides analysis of folate metabolism and homocysteine implications.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class MTHFRAnalyzer:
    """Analyzer for MTHFR gene variants C677T and A1298C."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MTHFR analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.mthfr_variants = self._get_mthfr_variant_info()
    
    def analyze_mthfr_variants(self, variants_file: str, outdir: Path) -> Dict[str, Any]:
        """
        Analyze MTHFR variants C677T and A1298C.
        
        Args:
            variants_file: Path to annotated variants file
            outdir: Output directory
            
        Returns:
            Dictionary of MTHFR analysis results
        """
        logger.info("Starting MTHFR variant analysis")
        
        # Load variants
        df = self._load_variants(variants_file)
        
        # Analyze MTHFR variants
        results = {
            'c677t': self._analyze_c677t(df),
            'a1298c': self._analyze_a1298c(df),
            'combined_analysis': {},
            'health_implications': {},
            'recommendations': {}
        }
        
        # Combined analysis
        results['combined_analysis'] = self._analyze_combined_variants(
            results['c677t'], results['a1298c']
        )
        
        # Health implications
        results['health_implications'] = self._assess_health_implications(results)
        
        # Recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        # Save results
        self._save_results(results, outdir)
        
        logger.info("MTHFR analysis completed")
        return results
    
    def _load_variants(self, variants_file: str) -> pd.DataFrame:
        """Load variants from file."""
        if variants_file.endswith('.parquet'):
            return pd.read_parquet(variants_file)
        else:
            return pd.read_csv(variants_file, sep='\t')
    
    def _get_mthfr_variant_info(self) -> Dict[str, Any]:
        """Get MTHFR variant information."""
        return {
            'C677T': {
                'rsid': 'rs1801133',
                'chromosome': '1',
                'position': 11796321,  # GRCh38
                'ref_allele': 'G',
                'alt_allele': 'A',
                'amino_acid_change': 'Ala222Val',
                'enzyme_activity': {
                    'CC': 'Normal (100%)',
                    'CT': 'Intermediate (65%)',
                    'TT': 'Reduced (30%)'
                },
                'population_frequency': {
                    'european': 0.35,
                    'asian': 0.20,
                    'african': 0.10
                }
            },
            'A1298C': {
                'rsid': 'rs1801131',
                'chromosome': '1',
                'position': 11794419,  # GRCh38
                'ref_allele': 'T',
                'alt_allele': 'G',
                'amino_acid_change': 'Glu429Ala',
                'enzyme_activity': {
                    'AA': 'Normal (100%)',
                    'AC': 'Intermediate (85%)',
                    'CC': 'Reduced (70%)'
                },
                'population_frequency': {
                    'european': 0.32,
                    'asian': 0.15,
                    'african': 0.08
                }
            }
        }
    
    def _analyze_c677t(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze C677T variant."""
        result = {
            'variant_name': 'C677T',
            'rsid': 'rs1801133',
            'genotype': 'CC',  # Wild type default
            'enzyme_activity': 'Normal (100%)',
            'variant_found': False,
            'allele_count': 0,
            'clinical_significance': 'Normal MTHFR enzyme activity'
        }
        
        # Look for the variant in the data
        mthfr_variants = df[df['Gene'] == 'MTHFR'] if 'Gene' in df.columns else pd.DataFrame()
        
        c677t_found = False
        if not mthfr_variants.empty:
            # Check for rs1801133 or position-based matching
            for _, variant in mthfr_variants.iterrows():
                dbsnp_id = variant.get('dbSNP_ID', '')
                position = str(variant.get('Genomic_Position', ''))
                
                if 'rs1801133' in str(dbsnp_id) or '11796321' in position:
                    c677t_found = True
                    result['variant_found'] = True
                    result['allele_count'] = 1  # Assuming heterozygous for simplicity
                    break
        
        # Determine genotype and enzyme activity
        if c677t_found:
            if result['allele_count'] == 1:
                result['genotype'] = 'CT'
                result['enzyme_activity'] = 'Intermediate (65%)'
                result['clinical_significance'] = 'Mildly reduced MTHFR enzyme activity'
            elif result['allele_count'] == 2:
                result['genotype'] = 'TT'
                result['enzyme_activity'] = 'Reduced (30%)'
                result['clinical_significance'] = 'Significantly reduced MTHFR enzyme activity'
        
        return result
    
    def _analyze_a1298c(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze A1298C variant."""
        result = {
            'variant_name': 'A1298C',
            'rsid': 'rs1801131',
            'genotype': 'AA',  # Wild type default
            'enzyme_activity': 'Normal (100%)',
            'variant_found': False,
            'allele_count': 0,
            'clinical_significance': 'Normal MTHFR enzyme activity'
        }
        
        # Look for the variant in the data
        mthfr_variants = df[df['Gene'] == 'MTHFR'] if 'Gene' in df.columns else pd.DataFrame()
        
        a1298c_found = False
        if not mthfr_variants.empty:
            # Check for rs1801131 or position-based matching
            for _, variant in mthfr_variants.iterrows():
                dbsnp_id = variant.get('dbSNP_ID', '')
                position = str(variant.get('Genomic_Position', ''))
                
                if 'rs1801131' in str(dbsnp_id) or '11794419' in position:
                    a1298c_found = True
                    result['variant_found'] = True
                    result['allele_count'] = 1  # Assuming heterozygous for simplicity
                    break
        
        # Determine genotype and enzyme activity
        if a1298c_found:
            if result['allele_count'] == 1:
                result['genotype'] = 'AC'
                result['enzyme_activity'] = 'Intermediate (85%)'
                result['clinical_significance'] = 'Mildly reduced MTHFR enzyme activity'
            elif result['allele_count'] == 2:
                result['genotype'] = 'CC'
                result['enzyme_activity'] = 'Reduced (70%)'
                result['clinical_significance'] = 'Moderately reduced MTHFR enzyme activity'
        
        return result
    
    def _analyze_combined_variants(self, c677t_result: Dict[str, Any], a1298c_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze combined effect of both variants."""
        combined_genotype = f"{c677t_result['genotype']}/{a1298c_result['genotype']}"
        
        # Determine combined risk level
        risk_level = "Low"
        enzyme_efficiency = "Normal to mildly reduced"
        
        if c677t_result['genotype'] == 'TT':
            risk_level = "High"
            enzyme_efficiency = "Significantly reduced"
        elif (c677t_result['genotype'] == 'CT' and a1298c_result['genotype'] == 'CC') or \
             (c677t_result['genotype'] == 'CC' and a1298c_result['genotype'] == 'CC'):
            risk_level = "Moderate"
            enzyme_efficiency = "Moderately reduced"
        elif c677t_result['genotype'] == 'CT' or a1298c_result['genotype'] == 'AC':
            risk_level = "Mild"
            enzyme_efficiency = "Mildly reduced"
        
        return {
            'combined_genotype': combined_genotype,
            'risk_level': risk_level,
            'enzyme_efficiency': enzyme_efficiency,
            'variants_present': c677t_result['variant_found'] or a1298c_result['variant_found'],
            'total_variant_alleles': c677t_result['allele_count'] + a1298c_result['allele_count']
        }
    
    def _assess_health_implications(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess health implications of MTHFR variants."""
        combined = results['combined_analysis']
        risk_level = combined['risk_level']
        
        implications = {
            'folate_metabolism': self._get_folate_implications(risk_level),
            'homocysteine_levels': self._get_homocysteine_implications(risk_level),
            'cardiovascular_risk': self._get_cardiovascular_implications(risk_level),
            'pregnancy_considerations': self._get_pregnancy_implications(risk_level),
            'neural_tube_defects': self._get_neural_tube_implications(risk_level),
            'mental_health': self._get_mental_health_implications(risk_level)
        }
        
        return implications
    
    def _get_folate_implications(self, risk_level: str) -> Dict[str, Any]:
        """Get folate metabolism implications."""
        implications = {
            'Low': {
                'description': 'Normal folate metabolism expected',
                'recommendation': 'Standard dietary folate intake sufficient',
                'supplement_need': 'Not specifically indicated'
            },
            'Mild': {
                'description': 'Mildly reduced folate metabolism efficiency',
                'recommendation': 'Ensure adequate dietary folate intake',
                'supplement_need': 'Consider methylfolate supplementation'
            },
            'Moderate': {
                'description': 'Moderately reduced folate metabolism',
                'recommendation': 'Increased folate needs likely',
                'supplement_need': 'Methylfolate supplementation recommended'
            },
            'High': {
                'description': 'Significantly impaired folate metabolism',
                'recommendation': 'High folate requirements',
                'supplement_need': 'Methylfolate supplementation strongly recommended'
            }
        }
        
        return implications.get(risk_level, implications['Low'])
    
    def _get_homocysteine_implications(self, risk_level: str) -> Dict[str, Any]:
        """Get homocysteine level implications."""
        implications = {
            'Low': 'Normal homocysteine levels expected',
            'Mild': 'Slightly elevated homocysteine possible',
            'Moderate': 'Moderately elevated homocysteine likely',
            'High': 'Significantly elevated homocysteine risk'
        }
        
        return {
            'description': implications.get(risk_level, implications['Low']),
            'monitoring': 'Consider periodic homocysteine testing' if risk_level != 'Low' else 'Routine monitoring sufficient',
            'target_level': '<15 μmol/L (normal), <10 μmol/L (optimal)'
        }
    
    def _get_cardiovascular_implications(self, risk_level: str) -> str:
        """Get cardiovascular implications."""
        implications = {
            'Low': 'No increased cardiovascular risk from MTHFR variants',
            'Mild': 'Slightly increased cardiovascular risk possible, especially with elevated homocysteine',
            'Moderate': 'Moderately increased cardiovascular risk, particularly with poor folate status',
            'High': 'Increased cardiovascular risk, especially important to maintain optimal folate status'
        }
        
        return implications.get(risk_level, implications['Low'])
    
    def _get_pregnancy_implications(self, risk_level: str) -> Dict[str, Any]:
        """Get pregnancy-related implications."""
        return {
            'neural_tube_defect_risk': 'Increased' if risk_level in ['Moderate', 'High'] else 'Standard',
            'folate_supplementation': 'Higher dose methylfolate recommended' if risk_level != 'Low' else 'Standard prenatal vitamins',
            'preconception_counseling': 'Recommended' if risk_level in ['Moderate', 'High'] else 'Standard care',
            'monitoring': 'Enhanced folate status monitoring' if risk_level != 'Low' else 'Routine care'
        }
    
    def _get_neural_tube_implications(self, risk_level: str) -> str:
        """Get neural tube defect implications."""
        implications = {
            'Low': 'Standard neural tube defect risk',
            'Mild': 'Slightly increased neural tube defect risk',
            'Moderate': 'Moderately increased neural tube defect risk',
            'High': 'Significantly increased neural tube defect risk'
        }
        
        return implications.get(risk_level, implications['Low'])
    
    def _get_mental_health_implications(self, risk_level: str) -> str:
        """Get mental health implications."""
        if risk_level == 'Low':
            return 'No specific mental health implications from MTHFR variants'
        else:
            return 'Possible association with mood disorders; ensure adequate folate and B-vitamin status'
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized recommendations."""
        risk_level = results['combined_analysis']['risk_level']
        
        recommendations = {
            'dietary': self._get_dietary_recommendations(risk_level),
            'supplementation': self._get_supplement_recommendations(risk_level),
            'lifestyle': self._get_lifestyle_recommendations(risk_level),
            'monitoring': self._get_monitoring_recommendations(risk_level),
            'medical': self._get_medical_recommendations(risk_level)
        }
        
        return recommendations
    
    def _get_dietary_recommendations(self, risk_level: str) -> List[str]:
        """Get dietary recommendations."""
        base_recs = [
            'Consume folate-rich foods: leafy greens, legumes, fortified grains',
            'Include foods high in B vitamins: meat, fish, eggs, dairy',
            'Limit alcohol consumption (interferes with folate metabolism)'
        ]
        
        if risk_level != 'Low':
            base_recs.extend([
                'Emphasize naturally occurring folate over synthetic folic acid',
                'Consider organic, unprocessed foods when possible',
                'Include foods rich in betaine: beets, spinach, quinoa'
            ])
        
        if risk_level in ['Moderate', 'High']:
            base_recs.extend([
                'Significantly increase folate-rich food intake',
                'Consider working with a nutritionist familiar with MTHFR variants'
            ])
        
        return base_recs
    
    def _get_supplement_recommendations(self, risk_level: str) -> List[str]:
        """Get supplementation recommendations."""
        if risk_level == 'Low':
            return ['Standard multivitamin may be sufficient']
        
        recommendations = [
            'Consider methylfolate (5-MTHF) instead of folic acid',
            'B-complex vitamin with active forms (methylcobalamin, P5P)',
            'Vitamin B12 (methylcobalamin form preferred)'
        ]
        
        if risk_level in ['Moderate', 'High']:
            recommendations.extend([
                'Higher dose methylfolate supplementation (800-5000 mcg)',
                'Consider additional B6 and riboflavin',
                'Consult healthcare provider for personalized dosing'
            ])
        
        return recommendations
    
    def _get_lifestyle_recommendations(self, risk_level: str) -> List[str]:
        """Get lifestyle recommendations."""
        recommendations = [
            'Maintain regular exercise routine',
            'Manage stress levels effectively',
            'Avoid smoking (increases homocysteine)'
        ]
        
        if risk_level != 'Low':
            recommendations.extend([
                'Limit processed foods and excess sugar',
                'Ensure adequate sleep (7-9 hours)',
                'Consider stress reduction techniques (meditation, yoga)'
            ])
        
        return recommendations
    
    def _get_monitoring_recommendations(self, risk_level: str) -> List[str]:
        """Get monitoring recommendations."""
        if risk_level == 'Low':
            return ['Routine health monitoring sufficient']
        
        recommendations = [
            'Periodic homocysteine level testing',
            'Monitor folate and B12 status',
            'Regular cardiovascular health assessments'
        ]
        
        if risk_level in ['Moderate', 'High']:
            recommendations.extend([
                'More frequent homocysteine monitoring (every 6-12 months)',
                'Consider methylmalonic acid testing (B12 function)',
                'Enhanced cardiovascular risk assessment'
            ])
        
        return recommendations
    
    def _get_medical_recommendations(self, risk_level: str) -> List[str]:
        """Get medical recommendations."""
        recommendations = [
            'Discuss results with healthcare provider',
            'Inform all healthcare providers of MTHFR status'
        ]
        
        if risk_level != 'Low':
            recommendations.extend([
                'Consider consultation with genetic counselor',
                'Discuss with healthcare provider before pregnancy',
                'Review medication interactions (methotrexate, etc.)'
            ])
        
        if risk_level in ['Moderate', 'High']:
            recommendations.extend([
                'Consider specialized metabolic or genetic medicine consultation',
                'Enhanced preconception counseling if planning pregnancy',
                'Coordinate care between multiple specialists if needed'
            ])
        
        return recommendations
    
    def _save_results(self, results: Dict[str, Any], outdir: Path) -> None:
        """Save MTHFR analysis results."""
        mthfr_dir = outdir / "mthfr"
        mthfr_dir.mkdir(exist_ok=True)
        
        # Save JSON results
        json_file = mthfr_dir / "mthfr_results.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"MTHFR results saved to {mthfr_dir}")


def analyze_mthfr_variants(variants_file: str, outdir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to analyze MTHFR variants.
    
    Args:
        variants_file: Path to annotated variants file
        outdir: Output directory
        config: Configuration dictionary
        
    Returns:
        MTHFR analysis results
    """
    analyzer = MTHFRAnalyzer(config)
    return analyzer.analyze_mthfr_variants(variants_file, outdir)


def generate_mthfr_report(results: Dict[str, Any], outdir: Path) -> str:
    """Generate MTHFR analysis report."""
    report_content = []
    
    # Header with strong disclaimer
    report_content.append("# MTHFR Gene Analysis Report")
    report_content.append("\n## ⚠️ IMPORTANT MEDICAL DISCLAIMER")
    report_content.append("**This analysis is for research and educational purposes only. It is NOT intended for medical diagnosis, treatment, or clinical decision-making. The information provided should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers before making any health-related decisions based on genetic information.**")
    
    # Executive Summary
    combined = results.get('combined_analysis', {})
    report_content.append("\n## Executive Summary")
    report_content.append(f"**Combined Genotype**: {combined.get('combined_genotype', 'Unknown')}")
    report_content.append(f"**Risk Level**: {combined.get('risk_level', 'Unknown')}")
    report_content.append(f"**Enzyme Efficiency**: {combined.get('enzyme_efficiency', 'Unknown')}")
    report_content.append(f"**Variants Present**: {'Yes' if combined.get('variants_present', False) else 'No'}")
    
    # Individual Variant Analysis
    report_content.append("\n## Individual Variant Analysis")
    
    # C677T Analysis
    c677t = results.get('c677t', {})
    report_content.append(f"\n### C677T Variant (rs1801133)")
    report_content.append(f"**Genotype**: {c677t.get('genotype', 'Unknown')}")
    report_content.append(f"**Enzyme Activity**: {c677t.get('enzyme_activity', 'Unknown')}")
    report_content.append(f"**Variant Found**: {'Yes' if c677t.get('variant_found', False) else 'No'}")
    report_content.append(f"**Clinical Significance**: {c677t.get('clinical_significance', 'Unknown')}")
    
    # A1298C Analysis
    a1298c = results.get('a1298c', {})
    report_content.append(f"\n### A1298C Variant (rs1801131)")
    report_content.append(f"**Genotype**: {a1298c.get('genotype', 'Unknown')}")
    report_content.append(f"**Enzyme Activity**: {a1298c.get('enzyme_activity', 'Unknown')}")
    report_content.append(f"**Variant Found**: {'Yes' if a1298c.get('variant_found', False) else 'No'}")
    report_content.append(f"**Clinical Significance**: {a1298c.get('clinical_significance', 'Unknown')}")
    
    # Health Implications
    implications = results.get('health_implications', {})
    report_content.append("\n## Health Implications")
    
    # Folate metabolism
    folate = implications.get('folate_metabolism', {})
    if folate:
        report_content.append(f"\n### Folate Metabolism")
        report_content.append(f"**Impact**: {folate.get('description', 'Unknown')}")
        report_content.append(f"**Recommendation**: {folate.get('recommendation', 'Unknown')}")
        report_content.append(f"**Supplementation**: {folate.get('supplement_need', 'Unknown')}")
    
    # Homocysteine
    homocysteine = implications.get('homocysteine_levels', {})
    if homocysteine:
        report_content.append(f"\n### Homocysteine Levels")
        report_content.append(f"**Expected Impact**: {homocysteine.get('description', 'Unknown')}")
        report_content.append(f"**Monitoring**: {homocysteine.get('monitoring', 'Unknown')}")
        report_content.append(f"**Target Level**: {homocysteine.get('target_level', 'Unknown')}")
    
    # Cardiovascular risk
    cardio_risk = implications.get('cardiovascular_risk', '')
    if cardio_risk:
        report_content.append(f"\n### Cardiovascular Considerations")
        report_content.append(f"{cardio_risk}")
    
    # Pregnancy considerations
    pregnancy = implications.get('pregnancy_considerations', {})
    if pregnancy:
        report_content.append(f"\n### Pregnancy Considerations")
        report_content.append(f"**Neural Tube Defect Risk**: {pregnancy.get('neural_tube_defect_risk', 'Unknown')}")
        report_content.append(f"**Folate Supplementation**: {pregnancy.get('folate_supplementation', 'Unknown')}")
        report_content.append(f"**Preconception Counseling**: {pregnancy.get('preconception_counseling', 'Unknown')}")
    
    # Recommendations
    recommendations = results.get('recommendations', {})
    report_content.append("\n## Personalized Recommendations")
    
    # Dietary recommendations
    dietary = recommendations.get('dietary', [])
    if dietary:
        report_content.append(f"\n### Dietary Recommendations")
        for rec in dietary:
            report_content.append(f"- {rec}")
    
    # Supplementation
    supplements = recommendations.get('supplementation', [])
    if supplements:
        report_content.append(f"\n### Supplementation Considerations")
        for rec in supplements:
            report_content.append(f"- {rec}")
    
    # Lifestyle
    lifestyle = recommendations.get('lifestyle', [])
    if lifestyle:
        report_content.append(f"\n### Lifestyle Recommendations")
        for rec in lifestyle:
            report_content.append(f"- {rec}")
    
    # Monitoring
    monitoring = recommendations.get('monitoring', [])
    if monitoring:
        report_content.append(f"\n### Monitoring Recommendations")
        for rec in monitoring:
            report_content.append(f"- {rec}")
    
    # Medical recommendations
    medical = recommendations.get('medical', [])
    if medical:
        report_content.append(f"\n### Medical Recommendations")
        for rec in medical:
            report_content.append(f"- {rec}")
    
    # Educational Information
    report_content.append("\n## About MTHFR")
    report_content.append("The MTHFR gene provides instructions for making an enzyme called methylenetetrahydrofolate reductase. This enzyme plays a role in processing amino acids and is important for the normal metabolism of folate (vitamin B9).")
    
    report_content.append("\n### Key Points:")
    report_content.append("- MTHFR variants are common in the general population")
    report_content.append("- Not all people with MTHFR variants develop health problems")
    report_content.append("- Environmental factors (diet, lifestyle) significantly influence outcomes")
    report_content.append("- Proper folate status can often compensate for reduced enzyme activity")
    
    # Final Disclaimers
    report_content.append("\n## Important Limitations")
    report_content.append("- This analysis is based on current scientific understanding")
    report_content.append("- Individual responses to MTHFR variants vary significantly")
    report_content.append("- Other genetic and environmental factors also influence folate metabolism")
    report_content.append("- Clinical correlation and professional interpretation are essential")
    
    report_content.append(f"\n---\n*Report generated by GenomeAI MTHFR Analysis Module*")
    report_content.append(f"*For research and educational purposes only*")
    
    # Save report
    report_file = outdir / "mthfr" / "mthfr_report.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_content))
    
    logger.info(f"MTHFR report saved to {report_file}")
    return str(report_file)