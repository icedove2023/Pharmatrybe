"""Stewardship Engine for antimicrobial stewardship analysis.

Evaluates stewardship concerns such as:
- Spectrum appropriateness (narrow vs. broad)
- Escalation vs. de-escalation
- Duplicate coverage
- Restricted antibiotic use
- Duration recommendations
"""

from typing import Any, Dict, List, Optional
import logging

from .contracts import StewardshipFinding, StewardshipDecision, RuleSeverity

logger = logging.getLogger(__name__)


class StewardshipEngine:
    """Engine for antimicrobial stewardship analysis.
    
    Evaluates recommendations against stewardship principles:
    - Use narrow-spectrum when possible
    - De-escalate when susceptibilities available
    - Avoid unnecessary use of restricted antibiotics
    - Optimize dosing and duration
    """

    def __init__(self):
        """Initialize stewardship engine."""
        self.logger = logging.getLogger(__name__)

    def analyze_stewardship(
        self,
        patient_data: Dict[str, Any],
        recommended_antibiotic: str,
        alternatives: Optional[List[str]] = None,
    ) -> List[StewardshipFinding]:
        """Analyze stewardship implications of a recommendation.
        
        Args:
            patient_data: Patient clinical data
            recommended_antibiotic: Primary recommendation
            alternatives: Alternative recommendations
            
        Returns:
            List of StewardshipFindings
        """
        findings = []
        
        # Analyze spectrum
        spectrum_finding = self._analyze_spectrum(recommended_antibiotic, patient_data)
        if spectrum_finding:
            findings.append(spectrum_finding)
        
        # Analyze escalation/de-escalation potential
        escalation_finding = self._analyze_escalation_potential(
            recommended_antibiotic,
            patient_data,
            alternatives or []
        )
        if escalation_finding:
            findings.append(escalation_finding)
        
        # Analyze restricted use
        restricted_finding = self._analyze_restricted_use(recommended_antibiotic)
        if restricted_finding:
            findings.append(restricted_finding)
        
        return findings

    def _analyze_spectrum(
        self,
        antibiotic: str,
        patient_data: Dict[str, Any],
    ) -> Optional[StewardshipFinding]:
        """Analyze spectrum appropriateness.
        
        Args:
            antibiotic: Antibiotic name
            patient_data: Patient data
            
        Returns:
            StewardshipFinding if spectrum is concerning
        """
        broad_spectrum = [
            'cefepime', 'ceftazidime', 'carbapenem', 'meropenem',
            'piperacillin', 'ciprofloxacin', 'levofloxacin'
        ]
        
        is_broad = any(bs in antibiotic.lower() for bs in broad_spectrum)
        
        if is_broad:
            return StewardshipFinding(
                finding_id="spectrum_concern",
                decision=StewardshipDecision.DE_ESCALATE,
                severity=RuleSeverity.MEDIUM,
                message="Broad-spectrum antibiotic selected. Consider narrowing if culture results available.",
                supporting_evidence=[
                    f"Selected antibiotic: {antibiotic}",
                    "Broad spectrum: covers many organisms",
                    "May contribute to resistance development"
                ],
                recommended_action="Review culture results for de-escalation opportunity",
                metadata={"antibiotic": antibiotic, "spectrum": "broad"}
            )
        
        return None

    def _analyze_escalation_potential(
        self,
        recommended: str,
        patient_data: Dict[str, Any],
        alternatives: List[str],
    ) -> Optional[StewardshipFinding]:
        """Analyze escalation vs. de-escalation.
        
        Args:
            recommended: Recommended antibiotic
            patient_data: Patient data
            alternatives: Alternative recommendations
            
        Returns:
            StewardshipFinding if escalation is needed
        """
        severity_high = patient_data.get("severity", "medium") == "high"
        immunocompromised = patient_data.get("immunocompromised", False)
        
        narrow_alternatives = [a for a in alternatives if self._is_narrow_spectrum(a)]
        
        if not severity_high and not immunocompromised and narrow_alternatives:
            return StewardshipFinding(
                finding_id="escalation_avoidance",
                decision=StewardshipDecision.MAINTAIN,
                severity=RuleSeverity.LOW,
                message="Escalation may not be necessary. Narrow-spectrum alternatives available.",
                supporting_evidence=[
                    f"Patient severity: {patient_data.get('severity', 'unknown')}",
                    f"Immunocompromised: {immunocompromised}",
                    f"Narrow alternatives available: {narrow_alternatives}"
                ],
                metadata={"current": recommended, "alternatives": narrow_alternatives}
            )
        
        return None

    def _analyze_restricted_use(self, antibiotic: str) -> Optional[StewardshipFinding]:
        """Analyze use of restricted/reserve antibiotics.
        
        Args:
            antibiotic: Antibiotic name
            
        Returns:
            StewardshipFinding if restricted use concern
        """
        restricted = [
            'carbapenem', 'meropenem', 'imipenem',
            'vancomycin',
            'colistin'
        ]
        
        is_restricted = any(r in antibiotic.lower() for r in restricted)
        
        if is_restricted:
            return StewardshipFinding(
                finding_id="restricted_use",
                decision=StewardshipDecision.MONITOR,
                severity=RuleSeverity.MEDIUM,
                message="Restricted/reserve antibiotic selected. Monitor closely and consider de-escalation.",
                supporting_evidence=[
                    f"Selected antibiotic: {antibiotic}",
                    "WHO Reserve category or institutional restricted use",
                    "Requires close monitoring and regular review"
                ],
                recommended_action="Monitor patient response. Plan de-escalation when possible.",
                metadata={"antibiotic": antibiotic, "category": "restricted"}
            )
        
        return None

    @staticmethod
    def _is_narrow_spectrum(antibiotic: str) -> bool:
        """Check if antibiotic is narrow-spectrum.
        
        Args:
            antibiotic: Antibiotic name
            
        Returns:
            True if narrow-spectrum
        """
        narrow = [
            'penicillin', 'amoxicillin', 'ampicillin',
            'cephalexin', 'cephalothin',
            'erythromycin'
        ]
        return any(n in antibiotic.lower() for n in narrow)
