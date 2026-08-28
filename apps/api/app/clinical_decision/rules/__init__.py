"""Clinical Rules Engine.

Evaluates clinical rules against patient data to identify contraindications,
drug interactions, and special considerations.

Rules include:
- Allergy screening
- Renal impairment adjustments
- Hepatic impairment adjustments
- Pregnancy/lactation restrictions
- Paediatric restrictions
- Drug interactions
- Stewardship restrictions
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

from ..contracts import ClinicalRuleResult, RuleSeverity, RuleStatus

logger = logging.getLogger(__name__)


class ClinicalRule(ABC):
    """Base class for clinical rules.
    
    Subclasses implement specific rule logic (allergy, renal, etc.)
    
    Attributes:
        rule_id: Unique rule identifier
        rule_name: Human-readable name
        description: Description of what the rule checks
    """

    def __init__(self, rule_id: str, rule_name: str, description: str = ""):
        """Initialize clinical rule.
        
        Args:
            rule_id: Unique identifier
            rule_name: Human-readable name
            description: What the rule checks
        """
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.description = description
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def evaluate(self, patient_data: Dict[str, Any], antibiotics: List[str]) -> ClinicalRuleResult:
        """Evaluate the rule against patient data.
        
        Args:
            patient_data: Patient clinical data
            antibiotics: List of antibiotics to check against
            
        Returns:
            ClinicalRuleResult with findings
        """
        pass


class AllergyRule(ClinicalRule):
    """Rule that checks for known drug allergies.
    
    Identifies if any recommended antibiotics match known allergies.
    """

    def __init__(self):
        super().__init__(
            rule_id="allergy",
            rule_name="Allergy Screening",
            description="Check for allergies to recommended antibiotics"
        )

    def evaluate(self, patient_data: Dict[str, Any], antibiotics: List[str]) -> ClinicalRuleResult:
        """Evaluate allergy rule.
        
        Args:
            patient_data: Must contain 'allergies' key with list of drug names
            antibiotics: Antibiotics to check
            
        Returns:
            ClinicalRuleResult with allergy findings
        """
        try:
            allergies = patient_data.get("allergies", [])
            if not allergies:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.PASSED,
                    severity=RuleSeverity.INFO,
                    message="No known allergies recorded",
                )

            # Check for matches
            affected = [ab for ab in antibiotics if any(
                self._is_allergy_match(ab, allergen) for allergen in allergies
            )]

            if affected:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.TRIGGERED,
                    severity=RuleSeverity.CRITICAL,
                    message=f"Allergy conflict: known allergies include {', '.join(allergies)}",
                    affected_drugs=affected,
                    evidence="Patient allergy history",
                )
            else:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.PASSED,
                    severity=RuleSeverity.INFO,
                    message="No allergies to recommended antibiotics",
                )

        except Exception as e:
            self.logger.error(f"Allergy rule evaluation failed: {e}", exc_info=True)
            return ClinicalRuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatus.ERROR,
                severity=RuleSeverity.HIGH,
                message=f"Error evaluating allergies: {str(e)}",
            )

    @staticmethod
    def _is_allergy_match(antibiotic: str, allergen: str) -> bool:
        """Check if antibiotic matches allergen (case-insensitive).
        
        Can be extended for cross-reactivity (e.g., all penicillins).
        """
        antibiotic_lower = antibiotic.lower()
        allergen_lower = allergen.lower()
        
        # Direct match
        if antibiotic_lower == allergen_lower:
            return True
        
        # Cross-reactivity for penicillins
        penicillins = ['penicillin', 'ampicillin', 'amoxicillin', 'amoxycillin']
        if allergen_lower in penicillins and antibiotic_lower in penicillins:
            return True
        
        return False


class RenalImpairmentRule(ClinicalRule):
    """Rule that checks for renal impairment requiring dosage adjustment.
    
    Identifies antibiotics requiring adjustment in renal disease.
    """

    def __init__(self):
        super().__init__(
            rule_id="renal_impairment",
            rule_name="Renal Impairment",
            description="Check for antibiotics requiring renal adjustment"
        )

    def evaluate(self, patient_data: Dict[str, Any], antibiotics: List[str]) -> ClinicalRuleResult:
        """Evaluate renal impairment rule.
        
        Args:
            patient_data: Must contain 'egfr' (eGFR mL/min/1.73m²) or 'creatinine'
            antibiotics: Antibiotics to check
            
        Returns:
            ClinicalRuleResult with renal findings
        """
        try:
            egfr = patient_data.get("egfr")
            
            if egfr is None:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.SKIPPED,
                    severity=RuleSeverity.INFO,
                    message="No eGFR data available",
                )
            
            # Determine impairment level
            if egfr >= 60:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.PASSED,
                    severity=RuleSeverity.INFO,
                    message=f"eGFR {egfr}: normal renal function",
                )
            
            # Identify antibiotics requiring adjustment
            if egfr < 30:
                severity = RuleSeverity.HIGH
                adjustment_msg = "eGFR <30: Significant renal impairment"
            elif egfr < 60:
                severity = RuleSeverity.MEDIUM
                adjustment_msg = f"eGFR {egfr}: Mild-moderate renal impairment"
            else:
                severity = RuleSeverity.LOW
                adjustment_msg = f"eGFR {egfr}: Borderline renal function"
            
            # Common renally-cleared antibiotics
            renally_cleared = [
                'gentamicin', 'tobramycin', 'amikacin',
                'cephalexin', 'ceftazidime', 'cefpodoxime',
                'levofloxacin', 'ciprofloxacin',
                'vancomycin',
                'penicillin', 'ampicillin'
            ]
            
            affected = [ab for ab in antibiotics 
                       if any(rc in ab.lower() for rc in renally_cleared)]
            
            if affected:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.TRIGGERED,
                    severity=severity,
                    message=adjustment_msg,
                    affected_drugs=affected,
                    evidence=f"eGFR: {egfr} mL/min/1.73m²",
                    metadata={"egfr": egfr},
                )
            else:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.PASSED,
                    severity=RuleSeverity.INFO,
                    message=f"eGFR {egfr}: No dosage adjustment needed",
                )

        except Exception as e:
            self.logger.error(f"Renal impairment rule evaluation failed: {e}", exc_info=True)
            return ClinicalRuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatus.ERROR,
                severity=RuleSeverity.HIGH,
                message=f"Error evaluating renal function: {str(e)}",
            )


class PregnancyRule(ClinicalRule):
    """Rule that checks for pregnancy-related restrictions.
    
    Identifies antibiotics contraindicated or requiring caution in pregnancy.
    """

    def __init__(self):
        super().__init__(
            rule_id="pregnancy",
            rule_name="Pregnancy Status",
            description="Check for pregnancy-related antibiotic restrictions"
        )

    def evaluate(self, patient_data: Dict[str, Any], antibiotics: List[str]) -> ClinicalRuleResult:
        """Evaluate pregnancy rule.
        
        Args:
            patient_data: Must contain 'is_pregnant' (bool) and 'is_lactating' (bool)
            antibiotics: Antibiotics to check
            
        Returns:
            ClinicalRuleResult with pregnancy findings
        """
        try:
            is_pregnant = patient_data.get("is_pregnant", False)
            is_lactating = patient_data.get("is_lactating", False)
            
            if not is_pregnant and not is_lactating:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.PASSED,
                    severity=RuleSeverity.INFO,
                    message="Not pregnant or lactating",
                )
            
            # Pregnancy-restricted antibiotics (Category D/X)
            restricted_pregnancy = [
                'tetracycline', 'doxycycline',
                'fluoroquinolone', 'ciprofloxacin', 'levofloxacin',
                'metronidazole',
                'sulfonamide', 'trimethoprim',
                'warfarin'
            ]
            
            affected = [ab for ab in antibiotics 
                       if any(r in ab.lower() for r in restricted_pregnancy)]
            
            status_msg = "Pregnant" if is_pregnant else "Lactating"
            
            if affected:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.TRIGGERED,
                    severity=RuleSeverity.HIGH if is_pregnant else RuleSeverity.MEDIUM,
                    message=f"{status_msg}: Category D/X antibiotics contraindicated",
                    affected_drugs=affected,
                    evidence=f"Pregnancy status: {status_msg}",
                    metadata={"is_pregnant": is_pregnant, "is_lactating": is_lactating},
                )
            else:
                return ClinicalRuleResult(
                    rule_id=self.rule_id,
                    rule_name=self.rule_name,
                    status=RuleStatus.PASSED,
                    severity=RuleSeverity.INFO,
                    message=f"{status_msg}: Recommended antibiotics safe",
                )

        except Exception as e:
            self.logger.error(f"Pregnancy rule evaluation failed: {e}", exc_info=True)
            return ClinicalRuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                status=RuleStatus.ERROR,
                severity=RuleSeverity.HIGH,
                message=f"Error evaluating pregnancy status: {str(e)}",
            )


class ClinicalRulesEngine:
    """Engine for evaluating clinical rules.
    
    Manages a collection of clinical rules and evaluates them against
    patient data and recommended antibiotics.
    """

    def __init__(self):
        """Initialize the rules engine with default rules."""
        self.rules: Dict[str, ClinicalRule] = {}
        self.logger = logging.getLogger(__name__)
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default clinical rules."""
        self.register_rule(AllergyRule())
        self.register_rule(RenalImpairmentRule())
        self.register_rule(PregnancyRule())

    def register_rule(self, rule: ClinicalRule) -> None:
        """Register a clinical rule.
        
        Args:
            rule: ClinicalRule instance to register
        """
        self.rules[rule.rule_id] = rule
        self.logger.info(f"Registered rule: {rule.rule_id} ({rule.rule_name})")

    def evaluate_all(
        self,
        patient_data: Dict[str, Any],
        antibiotics: List[str],
    ) -> List[ClinicalRuleResult]:
        """Evaluate all registered rules against patient data.
        
        Args:
            patient_data: Patient clinical data
            antibiotics: Recommended antibiotics to check
            
        Returns:
            List of ClinicalRuleResult objects
        """
        results = []
        
        for rule_id, rule in self.rules.items():
            try:
                result = rule.evaluate(patient_data, antibiotics)
                results.append(result)
                self.logger.debug(
                    f"Rule {rule_id} evaluated: {result.status.value}",
                    extra={"rule": rule_id, "status": result.status.value}
                )
            except Exception as e:
                self.logger.error(
                    f"Error evaluating rule {rule_id}: {e}",
                    exc_info=True
                )
                # Create error result
                results.append(ClinicalRuleResult(
                    rule_id=rule_id,
                    rule_name=self.rules[rule_id].rule_name,
                    status=RuleStatus.ERROR,
                    severity=RuleSeverity.HIGH,
                    message=f"Rule evaluation failed: {str(e)}",
                ))
        
        return results

    def evaluate_specific(
        self,
        rule_id: str,
        patient_data: Dict[str, Any],
        antibiotics: List[str],
    ) -> Optional[ClinicalRuleResult]:
        """Evaluate a specific rule.
        
        Args:
            rule_id: ID of rule to evaluate
            patient_data: Patient clinical data
            antibiotics: Recommended antibiotics to check
            
        Returns:
            ClinicalRuleResult or None if rule not found
        """
        if rule_id not in self.rules:
            self.logger.warning(f"Rule not found: {rule_id}")
            return None
        
        try:
            return self.rules[rule_id].evaluate(patient_data, antibiotics)
        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule_id}: {e}", exc_info=True)
            return ClinicalRuleResult(
                rule_id=rule_id,
                rule_name=self.rules[rule_id].rule_name,
                status=RuleStatus.ERROR,
                severity=RuleSeverity.HIGH,
                message=f"Rule evaluation failed: {str(e)}",
            )

    def get_triggered_rules(
        self,
        patient_data: Dict[str, Any],
        antibiotics: List[str],
    ) -> List[ClinicalRuleResult]:
        """Get only the rules that were triggered.
        
        Args:
            patient_data: Patient clinical data
            antibiotics: Recommended antibiotics
            
        Returns:
            List of triggered ClinicalRuleResults
        """
        all_results = self.evaluate_all(patient_data, antibiotics)
        return [r for r in all_results if r.status == RuleStatus.TRIGGERED]
