# Knowledge Plugin Extensibility Report

**Purpose:** Assessment of SDK extensibility for future Knowledge Plugin implementations

**Status:** ✅ PRODUCTION-READY

**Date:** August 2026

---

## Executive Summary

The Knowledge Plugin SDK is fully extensible and ready to support multiple future knowledge sources without requiring platform core modifications.

### Extensibility Assessment

| Future Plugin | Type | Status | Effort | Timeline |
|---------------|------|--------|--------|----------|
| WHO AWaRe | Knowledge | ✅ Extensible | 2-3 weeks | Stage 5.2 |
| NICE Guidelines | Knowledge | ✅ Extensible | 2-3 weeks | Stage 5.3 |
| IDSA Standards | Knowledge | ✅ Extensible | 2-3 weeks | Stage 5.3 |
| Hospital Policy | Knowledge | ✅ Extensible | 1-2 weeks | Stage 5.4 |
| Drug Database | Knowledge | ✅ Extensible | 1-2 weeks | Stage 5.5 |
| Local AMR Database | Knowledge | ✅ Extensible | 2-4 weeks | Stage 5.5 |
| External API (CDC) | Knowledge | ✅ Extensible | 2-3 weeks | Stage 5.6 |

**Key Finding:** ✅ **No platform changes required for any future plugin.**

---

## Part 1: Architecture Flexibility

### Plugin Contract is Minimal and Universal

The `KnowledgePlugin` abstract class defines only essential operations:

```python
class KnowledgePlugin(BasePlugin):
    """Minimal contract for all knowledge plugins."""
    
    @abstractmethod
    def connect(self) -> None:
        """Connect to knowledge source."""
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from knowledge source."""
    
    @abstractmethod
    def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Text-based search."""
    
    @abstractmethod
    def query(self, criteria: Dict) -> Dict:
        """Structured query."""
    
    @abstractmethod
    def supported_domains(self) -> List[str]:
        """Clinical domains this plugin covers."""
    
    @abstractmethod
    def knowledge_version(self) -> str:
        """Version of underlying knowledge data."""
```

### Why This Enables Extensibility

1. **No Domain-Specific Logic:**
   - Plugin contract doesn't assume any specific knowledge domain
   - Works equally for WHO, NICE, IDSA, hospital policies, etc.
   - Methods are agnostic to clinical content

2. **Flexible Output Format:**
   - `search()` and `query()` return generic dicts
   - Each plugin can structure its output independently
   - Explainability Engine extracts key fields (source, citation, evidence_level)
   - Extra fields are preserved for plugin-specific use

3. **No Orchestration Changes:**
   - Plugin discovery is purely registry-based
   - Workflow Manager treats all KnowledgePlugins identically
   - No plugin-specific execution logic needed
   - New plugins just need `plugin_id`, `plugin_name`, `plugin_type`

4. **No Routing Changes:**
   - `PluginRoutingPolicy` routes by domain capability
   - Doesn't care which plugin implements the domain
   - Multiple plugins can claim the same domain (all execute)
   - AUTO mode will discover and use new plugins automatically

---

## Part 2: WHO AWaRe Knowledge Plugin (First Implementation)

### Plugin Structure

```python
from app.plugins.base.knowledge_plugin import KnowledgePlugin
from app.plugins.base.plugin import PluginType, PluginMetadata, PluginHealth
from typing import Any, Dict, List, Optional
import psycopg2
from datetime import datetime


class WHOAWaRePlugin(KnowledgePlugin):
    """WHO Access/Watch/Reserve (AWaRe) Classification Plugin."""
    
    def __init__(self):
        self._connection = None
        self._cursor = None
    
    # ========== Properties ==========
    
    @property
    def plugin_id(self) -> str:
        return "who_aware"
    
    @property
    def plugin_name(self) -> str:
        return "WHO AWaRe Classification"
    
    @property
    def plugin_version(self) -> str:
        return "0.1.0"
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE
    
    @property
    def plugin_description(self) -> str:
        return "Provides WHO Access/Watch/Reserve antibiotic classification"
    
    @property
    def author(self) -> str:
        return "WHO / Clinical Team"
    
    @property
    def capabilities(self) -> List[str]:
        return ["antibiotic_classification", "stewardship_evidence"]
    
    @property
    def dependencies(self) -> List[str]:
        return ["postgresql", "python3.9+"]
    
    # ========== Lifecycle Methods ==========
    
    def initialize(self) -> None:
        """Initialize plugin at startup."""
        # Load WHO data into memory or connect to database
        self._who_data = self._load_who_data()
    
    def shutdown(self) -> None:
        """Shutdown plugin at unload."""
        if self._connection:
            self._connection.close()
        self._who_data = None
    
    def configure(self, configuration: Dict[str, Any]) -> None:
        """Configure with runtime parameters."""
        self.db_host = configuration.get("db_host", "localhost")
        self.db_port = configuration.get("db_port", 5432)
        self.db_name = configuration.get("db_name", "who_aware")
        self.db_user = configuration.get("db_user", "")
        self.db_password = configuration.get("db_password", "")
        self.cache_ttl = configuration.get("cache_ttl_seconds", 3600)
        
        if not self.db_user:
            raise ValueError("db_user is required in configuration")
    
    def validate(self) -> bool:
        """Validate plugin readiness."""
        return self._who_data is not None and self._connection is not None
    
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            plugin_id=self.plugin_id,
            plugin_name=self.plugin_name,
            plugin_version=self.plugin_version,
            plugin_type=self.plugin_type,
            description=self.plugin_description,
            author=self.author,
            capabilities=self.capabilities,
            dependencies=self.dependencies
        )
    
    def health(self) -> PluginHealth:
        """Return health status."""
        is_healthy = self._connection is not None and self._who_data is not None
        return PluginHealth(
            healthy=is_healthy,
            status="connected" if is_healthy else "disconnected",
            message=None,
            timestamp=datetime.now()
        )
    
    # ========== Connection Management ==========
    
    def connect(self) -> None:
        """Connect to WHO database."""
        try:
            self._connection = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                timeout=5
            )
            self._cursor = self._connection.cursor()
        except psycopg2.OperationalError as exc:
            raise ConnectionError(f"Failed to connect to WHO database: {exc}")
    
    def disconnect(self) -> None:
        """Disconnect from WHO database."""
        if self._cursor:
            self._cursor.close()
        if self._connection:
            self._connection.close()
        self._connection = None
        self._cursor = None
    
    # ========== Query Methods ==========
    
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search WHO AWaRe by antibiotic name.
        
        Args:
            query: Antibiotic name to search for (e.g., "Amoxicillin", "Ceftriaxone")
            filters: Optional filters (not used for WHO, but kept for interface compliance)
        
        Returns:
            List of WHO AWaRe results
        """
        antibiotic_name = query.lower().strip()
        
        try:
            # Query WHO database
            self._cursor.execute(
                """
                SELECT category, route, indication, access_link 
                FROM who_aware 
                WHERE LOWER(drug_name) = %s
                """,
                (antibiotic_name,)
            )
            
            result = self._cursor.fetchone()
            
            if not result:
                return []  # No match found
            
            category, route, indication, access_link = result
            
            return [{
                "source": "WHO AWaRe",
                "guideline_id": f"who_aware:{antibiotic_name}",
                "antibiotic": query,
                "category": category,  # "Access", "Watch", or "Reserve"
                "route": route,  # "Oral", "Parenteral", etc.
                "indication": indication,
                "evidence_level": "HIGH",  # WHO is authoritative
                "recommendation": f"{query} is in WHO AWaRe {category} category",
                "citation": "WHO Access/Watch/Reserve (AWaRe) Classification",
                "metadata": {
                    "version": "WHO AWaRe 2023",
                    "year": 2023,
                    "access_link": access_link,
                    "knowledge_source": "https://www.who.int/publications/i/item/AWaRe"
                }
            }]
        
        except Exception as exc:
            raise ConnectionError(f"WHO database query failed: {exc}")
    
    def query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Query WHO AWaRe with structured criteria.
        
        Args:
            criteria: Dictionary with keys like:
                - "antibiotic": str (drug name)
                - "category": str (optional filter: "Access", "Watch", "Reserve")
                - "route": str (optional filter: "Oral", "Parenteral")
        
        Returns:
            Structured WHO AWaRe result
        """
        antibiotic = criteria.get("antibiotic", "").lower().strip()
        
        if not antibiotic:
            return {}  # Invalid criteria
        
        try:
            self._cursor.execute(
                """
                SELECT category, route, indication, access_link 
                FROM who_aware 
                WHERE LOWER(drug_name) = %s
                """,
                (antibiotic,)
            )
            
            result = self._cursor.fetchone()
            
            if not result:
                return {}  # No match
            
            category, route, indication, access_link = result
            
            return {
                "source": "WHO AWaRe",
                "guideline_id": f"who_aware:{antibiotic}",
                "antibiotic": criteria.get("antibiotic"),
                "category": category,
                "route": route,
                "indication": indication,
                "evidence_level": "HIGH",
                "recommendation": f"WHO classifies {criteria.get('antibiotic')} as {category}",
                "citation": "WHO Access/Watch/Reserve (AWaRe) Classification",
                "metadata": {
                    "version": "WHO AWaRe 2023",
                    "access_link": access_link
                }
            }
        
        except Exception as exc:
            raise ValueError(f"WHO query failed: {exc}")
    
    # ========== Domain Methods ==========
    
    def supported_domains(self) -> List[str]:
        """WHO AWaRe applies to all infection types."""
        return [
            "respiratory",
            "gastrointestinal",
            "urinary_tract",
            "wound",
            "bloodstream",
            "meningitis",
            "general"  # Applies broadly to all
        ]
    
    def knowledge_version(self) -> str:
        """Return WHO data version."""
        return "WHO AWaRe 2023"
    
    # ========== Helper Methods ==========
    
    def _load_who_data(self) -> Dict[str, Any]:
        """Load WHO data at initialization."""
        # Could be:
        # 1. In-memory dict loaded from JSON
        # 2. Database connection
        # 3. Cache layer
        return {}
```

### WHO Plugin Registration

```python
# In plugin registry
registry.register_plugin(
    plugin_id="who_aware",
    plugin_instance=WHOAWaRePlugin(),
    configuration={
        "db_host": "localhost",
        "db_port": 5432,
        "db_name": "who_aware",
        "db_user": os.getenv("WHO_DB_USER"),
        "db_password": os.getenv("WHO_DB_PASSWORD")
    }
)
```

### WHO Plugin Usage (in Workflow)

```
# Clinician requests decision for respiratory infection
Request:
  domain: "respiratory"
  execution_mode: "AUTO"

Routing:
  → Find plugins with "respiratory" domain
  → WHO AWaRe supports "respiratory" ✓
  → Select WHO plugin

Execution:
  → query = antibiotic name (from request)
  → plugin.search(query)
  → WHO database lookup
  → Return category (Access/Watch/Reserve)

Explanation:
  → Include WHO category in evidence
  → Link to WHO documentation
  → Cite as authoritative source
```

---

## Part 3: NICE Guidelines Knowledge Plugin (Second Implementation)

### Plugin Structure

```python
class NICEGuidelinesPlugin(KnowledgePlugin):
    """NICE Clinical Guidelines Knowledge Plugin."""
    
    def __init__(self):
        self._nice_db = None
        self._cache = {}
    
    @property
    def plugin_id(self) -> str:
        return "nice_guidelines"
    
    @property
    def plugin_name(self) -> str:
        return "NICE Guidelines"
    
    def supported_domains(self) -> List[str]:
        return [
            "respiratory",      # Respiratory infections
            "gastrointestinal", # GI infections
            "urinary_tract",   # UTI
            "general"          # Cross-cutting guidelines
        ]
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search NICE guidelines by infection or indication.
        
        query: Infection type (e.g., "community-acquired pneumonia")
        """
        indication = query.lower()
        
        # Search NICE database
        results = self._nice_db.search_by_indication(indication)
        
        if not results:
            return []
        
        return [{
            "source": "NICE Guidelines",
            "guideline_id": f"nice:{indication}:{result['priority']}",
            "recommendation": result["recommendation"],
            "evidence_level": "HIGH",
            "citation": f"NICE {result['guideline_name']} ({result['year']})",
            "metadata": {
                "nice_url": result["url"],
                "evidence_quality": result["evidence_quality"],
                "last_updated": result["last_updated"]
            }
        } for result in results]
    
    def query(self, criteria: Dict) -> Dict:
        """Query NICE guidelines with structured criteria.
        
        criteria: {
            "indication": str,
            "patient_factors": {...},
            "priority": "first_line" | "second_line"
        }
        """
        indication = criteria.get("indication")
        priority = criteria.get("priority", "first_line")
        
        result = self._nice_db.query_guideline(indication, priority)
        
        if not result:
            return {}
        
        return {
            "source": "NICE Guidelines",
            "guideline_id": f"nice:{indication}:{priority}",
            "recommendation": result["recommendation"],
            "evidence_level": "HIGH",
            "citation": f"NICE {result['guideline_name']}",
            "metadata": result.get("metadata", {})
        }
```

### NICE Plugin Features

✅ **Independent from WHO Plugin:**
- No shared code
- No shared database
- No hardcoded references to WHO

✅ **Discoverable Automatically:**
- Registers with domain "respiratory", "gastrointestinal", etc.
- AUTO routing finds it by domain

✅ **Runs Alongside WHO:**
- Both WHO and NICE execute in same request
- Results aggregated separately in context
- Explainability includes both

---

## Part 4: IDSA Standards Plugin (Third Implementation)

### Similar Structure

```python
class IDSAStandardsPlugin(KnowledgePlugin):
    """IDSA Infectious Diseases Society of America Standards."""
    
    @property
    def plugin_id(self) -> str:
        return "idsa_standards"
    
    def supported_domains(self) -> List[str]:
        return ["respiratory", "bloodstream", "general"]
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search IDSA guidelines by infection type."""
        # Query IDSA database
        # Return structured results
        ...
    
    # All other methods follow same pattern
```

### Execution in HYBRID Mode

```
Request: domain=respiratory, execution_mode=HYBRID

Routing:
  → WHO AWaRe ✓
  → NICE ✓
  → IDSA ✓
  → SOAR/GSK ✓
  → ARMD ✓

Execution (concurrent):
  → WHO search → Access category
  → NICE search → First-line recommendation
  → IDSA search → IDSA guideline
  → SOAR search → Probability 0.92
  → ARMD search → Resistance risk

Context:
  knowledge_outputs: [WHO, NICE, IDSA]
  prediction_outputs: [SOAR, ARMD]

Explanation:
  "WHO Access category, NICE recommends, IDSA concurs,
   ML model confidence 92%, no resistance history"
```

---

## Part 5: Hospital Policy Plugin (Lower Priority)

### Example: Local Stewardship Rules

```python
class HospitalPolicyPlugin(KnowledgePlugin):
    """Hospital-specific antibiotic policies."""
    
    @property
    def plugin_id(self) -> str:
        return "hospital_policy"
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search hospital policies for antibiotic.
        
        query: Antibiotic name
        filters: {"department": "ICU", "patient_type": "immunocompromised"}
        """
        antibiotic = query.lower()
        department = filters.get("department") if filters else None
        
        # Look up hospital policy
        policy = self._hospital_db.get_policy(antibiotic, department)
        
        if not policy:
            return []
        
        return [{
            "source": "Hospital Policy",
            "guideline_id": f"hospital:{antibiotic}:{department}",
            "recommendation": policy["allowed"] and "Approved for use" or "Restricted",
            "citation": f"Hospital Stewardship Policy v{policy['version']}",
            "metadata": {
                "approval_required": policy.get("approval_required"),
                "preferred_alternative": policy.get("preferred_alternative"),
                "restriction_reason": policy.get("restriction_reason")
            }
        }]
```

---

## Part 6: Drug Database Plugin

### Example: Pharmacokinetics and Drug Information

```python
class DrugDatabasePlugin(KnowledgePlugin):
    """Pharmaceutical drug database for dosing and interactions."""
    
    def query(self, criteria: Dict) -> Dict:
        """Query drug information.
        
        criteria: {
            "drug": "amoxicillin",
            "patient": {"renal_function": "moderate", "age": 65},
            "interaction_check": ["warfarin", "metformin"]
        }
        """
        drug = criteria.get("drug")
        patient_data = criteria.get("patient", {})
        interactions = criteria.get("interaction_check", [])
        
        # Get drug info
        drug_info = self._drug_db.get_drug(drug)
        
        # Calculate adjusted dosing
        dose = self._calculate_dose(drug_info, patient_data)
        
        # Check interactions
        interactions_found = self._check_interactions(drug, interactions)
        
        return {
            "source": "Drug Database",
            "guideline_id": f"drug:{drug}",
            "recommendation": f"Dosing: {dose}, No significant interactions" if not interactions_found else f"Warning: {interactions_found}",
            "evidence_level": "HIGH",
            "citation": "Pharmaceutical Database v2.1",
            "contraindications": drug_info.get("contraindications", []),
            "metadata": {
                "dosing": dose,
                "interactions": interactions_found,
                "renal_adjustment": drug_info.get("renal_adjustment", None)
            }
        }
```

---

## Part 7: External API Plugin (Future)

### Example: CDC Resistance Data

```python
class CDCResistancePlugin(KnowledgePlugin):
    """CDC National Healthcare Safety Network (NHSN) resistance data."""
    
    def connect(self) -> None:
        """Connect to CDC API."""
        self.api_client = CDCAPIClient(
            api_key=self.api_key,
            timeout=self.timeout_ms / 1000
        )
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search CDC resistance surveillance data.
        
        query: Organism name (e.g., "E. coli")
        """
        organism = query
        region = filters.get("region") if filters else "national"
        
        try:
            # Call CDC API
            data = self.api_client.get_resistance(
                organism=organism,
                region=region,
                year=datetime.now().year
            )
            
            return [{
                "source": "CDC NHSN",
                "guideline_id": f"cdc:{organism}:{region}",
                "recommendation": f"{organism} resistance rates: {data['resistance_percent']}%",
                "evidence_level": "MEDIUM",  # Epidemiological data
                "citation": "CDC National Healthcare Safety Network",
                "metadata": {
                    "region": region,
                    "year": datetime.now().year,
                    "data_source": "NHSN",
                    "resistance_genes": data.get("resistance_genes")
                }
            }]
        
        except Exception as exc:
            raise ConnectionError(f"CDC API error: {exc}")
```

---

## Part 8: Extensibility Assessment Summary

### What Remains Unchanged

✅ **Platform Core:**
- Workflow Manager (no changes needed)
- Plugin Manager (no changes needed)
- PluginRoutingPolicy (no changes needed)
- ClinicalIntelligencePipeline (no changes needed)
- Decision Fusion Engine (no changes needed)
- Explainability Engine (no changes needed)

✅ **Contracts:**
- BasePlugin interface unchanged
- KnowledgePlugin interface unchanged
- PluginExecutionResult format unchanged
- ClinicalDecisionContext format unchanged

✅ **Orchestration:**
- Registry-based discovery unchanged
- Execution isolation unchanged
- Error handling unchanged
- Result aggregation unchanged

### What is Extensible

✅ **New Knowledge Plugins:**
- Can be added without modifying platform
- Just implement KnowledgePlugin interface
- Register with plugin ID, name, capabilities
- All routing/execution happens automatically

✅ **Knowledge Sources:**
- Database (PostgreSQL, MongoDB, etc.)
- REST APIs (WHO, CDC, NICE APIs)
- File systems (local guidelines)
- Cache layers (Redis, Memcached)
- Message brokers (event-driven updates)

✅ **Output Formats:**
- Each plugin defines its own output structure
- Platform extracts key fields (source, citation, evidence_level)
- Extra fields preserved for plugin-specific use

✅ **Deployment Models:**
- Embedded (in-process)
- Sidecar (local service)
- Remote (distributed service)
- Cloud (SaaS integration)

---

## Part 9: Roadmap for Future Implementations

### Phase 5.2 (Next Phase)
- ✅ WHO AWaRe Plugin
- Timeline: 2-3 weeks
- Effort: 1 developer
- Blocker: None

### Phase 5.3
- ✅ NICE Guidelines Plugin
- ✅ IDSA Standards Plugin
- Timeline: 3-4 weeks
- Effort: 2 developers
- Blocker: None

### Phase 5.4
- ✅ Hospital Policy Plugin
- Timeline: 1-2 weeks
- Effort: 1 developer
- Blocker: Hospital system access setup

### Phase 5.5
- ✅ Drug Database Plugin
- ✅ Local AMR Database Plugin
- Timeline: 3-4 weeks
- Effort: 1-2 developers
- Blocker: None

### Phase 5.6+
- ✅ CDC NHSN Plugin
- ✅ External API Plugins
- Timeline: 2-3 weeks per plugin
- Effort: 1 developer per plugin
- Blocker: API access/authentication

---

## Part 10: Implementation Template

### Standard Knowledge Plugin Checklist

**For implementing any new Knowledge Plugin:**

```
□ Create class that inherits from KnowledgePlugin
□ Implement @property decorators:
  □ plugin_id
  □ plugin_name
  □ plugin_version
  □ plugin_type (set to PluginType.KNOWLEDGE)
  □ plugin_description
  □ author
  □ capabilities
  □ dependencies

□ Implement lifecycle methods:
  □ initialize()
  □ shutdown()
  □ configure()
  □ validate()
  □ metadata()
  □ health()

□ Implement connection methods:
  □ connect()
  □ disconnect()

□ Implement query methods:
  □ search()
  □ query()

□ Implement domain methods:
  □ supported_domains()
  □ knowledge_version()

□ Register with Plugin Registry
□ Configure with environment variables
□ Write unit tests
□ Test in HYBRID mode with other plugins
□ Document output format
□ Verify Explainability Engine integration
□ Add to deployment configuration
```

---

## Summary of Extensibility

| Aspect | Status | Evidence |
|--------|--------|----------|
| **Minimal Plugin Contract** | ✅ | 10 abstract methods only |
| **No Domain-Specific Logic** | ✅ | Plugin agnostic to content |
| **Generic Output Format** | ✅ | Dicts with flexible fields |
| **Registry-Driven Discovery** | ✅ | No hardcoded plugin names |
| **Automatic Routing** | ✅ | Domain-based selection |
| **Concurrent Execution** | ✅ | Multiple plugins same request |
| **Error Isolation** | ✅ | Plugin failures don't cascade |
| **No Platform Changes** | ✅ | Core architecture unchanged |
| **Future-Ready** | ✅ | 7+ planned plugins assessed |

---

**End of Extensibility Report**

*Knowledge Plugin SDK is extensible without platform modifications. Ready for multi-source implementation strategy.*
