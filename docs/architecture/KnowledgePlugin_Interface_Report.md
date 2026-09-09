# Knowledge Plugin Interface Report

**Purpose:** Detailed review of Knowledge Plugin SDK interfaces and contracts

**Status:** ✅ VALIDATED

---

## Executive Summary

The Knowledge Plugin SDK provides a well-defined abstract interface that:
- ✅ Inherits all BasePlugin lifecycle methods
- ✅ Adds knowledge-specific connection management
- ✅ Provides structured search and query methods
- ✅ Supports flexible output formats
- ✅ Enables version tracking and domain filtering

---

## Part 1: Inherited BasePlugin Interface

All Knowledge Plugins inherit from `BasePlugin` and must implement:

### Core Properties (Required)

```python
class KnowledgePlugin(BasePlugin):
    
    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique plugin identifier.
        
        Example: "who_aware", "nice_guidelines", "idsa_standards"
        Used for: registry lookup, routing, audit trails
        """
    
    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Human-readable plugin name.
        
        Example: "WHO AWaRe Classification"
        Used for: UI display, logging
        """
    
    @property
    @abstractmethod
    def plugin_version(self) -> str:
        """Plugin version string (semantic versioning).
        
        Example: "0.1.0", "1.0.0"
        Used for: auditing, compatibility checks
        """
    
    @property
    @abstractmethod
    def plugin_type(self) -> PluginType:
        """Plugin category type.
        
        Must be: PluginType.KNOWLEDGE
        Used for: routing, execution logic
        """
    
    @property
    @abstractmethod
    def plugin_description(self) -> str:
        """Plugin description.
        
        Example: "Provides WHO AWaRe antibiotic classification"
        Used for: documentation, discovery
        """
    
    @property
    @abstractmethod
    def author(self) -> str:
        """Plugin author or owner.
        
        Example: "WHO", "Clinical Team"
        Used for: accountability, maintenance
        """
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Plugin capabilities exposed to the platform.
        
        Example: ["access_classification", "resistance_data", "recommendations"]
        Used for: AUTO routing (domain inference)
        """
    
    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """Plugin dependencies declared by the plugin.
        
        Example: ["python3.9+", "postgresql"]
        Used for: deployment validation
        """
```

### Lifecycle Methods (Required)

```python
@abstractmethod
def initialize(self) -> None:
    """Initialize plugin resources at startup.
    
    Called once at plugin load time.
    
    Responsibilities:
    - Load configuration
    - Prepare data structures
    - Pre-allocate resources
    
    Raises:
    - Exception if initialization fails (plugin will not be loaded)
    """
    raise NotImplementedError


@abstractmethod
def shutdown(self) -> None:
    """Shutdown plugin resources cleanly.
    
    Called once at plugin unload time.
    
    Responsibilities:
    - Release resources
    - Close file handles
    - Clean up temporary data
    
    Note: Should not raise exceptions
    """
    raise NotImplementedError


@abstractmethod
def configure(self, configuration: Dict[str, Any]) -> None:
    """Configure plugin with runtime parameters.
    
    Called after initialize() with configuration dict.
    
    Parameters:
        configuration: Dict with plugin-specific settings
        
        Example:
        {
            "database_url": "postgresql://...",
            "api_key": "...",
            "timeout_ms": 5000
        }
    
    Responsibilities:
    - Apply configuration
    - Validate settings
    - Open connections if needed
    
    Raises:
    - ValueError if configuration is invalid
    """
    raise NotImplementedError


@abstractmethod
def validate(self) -> bool:
    """Validate plugin readiness and health.
    
    Called to verify plugin is functional.
    
    Returns:
    - True if plugin is ready to handle requests
    - False if plugin should not be used
    
    Used for:
    - Pre-request validation
    - Health checks
    - Graceful degradation
    """
    raise NotImplementedError


@abstractmethod
def metadata(self) -> PluginMetadata:
    """Return structured plugin metadata.
    
    Returns:
        PluginMetadata with all identifying information
    """
    raise NotImplementedError


@abstractmethod
def health(self) -> PluginHealth:
    """Return structured health status.
    
    Returns:
        PluginHealth with:
        - healthy: bool
        - status: str (e.g., "ok", "degraded", "unavailable")
        - message: Optional error message
        - timestamp: datetime of health check
    """
    raise NotImplementedError
```

---

## Part 2: Knowledge-Specific Interface

Knowledge Plugins extend BasePlugin with connection and query methods:

### Connection Management

```python
@abstractmethod
def connect(self) -> None:
    """Connect to the knowledge source.
    
    Establishes connections to:
    - Database
    - REST API
    - File system
    - Cache layer
    - Message broker (if needed)
    
    Called during initialize() or on-demand.
    
    Responsibilities:
    - Test connectivity
    - Establish pooled connections
    - Prepare query builders
    
    Raises:
    - ConnectionError if source is unreachable
    - TimeoutError if connection attempt times out
    """
    raise NotImplementedError


@abstractmethod
def disconnect(self) -> None:
    """Disconnect from the knowledge source.
    
    Closes all connections established in connect().
    
    Called during shutdown() or graceful degradation.
    
    Responsibilities:
    - Close database connections
    - Flush any pending writes
    - Release connections back to pools
    
    Note: Should not raise exceptions; used in cleanup
    """
    raise NotImplementedError
```

### Query Methods

```python
@abstractmethod
def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Search the knowledge source with a text query.
    
    Parameters:
        query: The search text (e.g., "Amoxicillin", "respiratory infection")
        filters: Optional criteria for narrowing results
        
        Example filters:
        {
            "domain": "respiratory",
            "antibiotic_class": "beta_lactam",
            "patient_age": 65,
            "renal_function": "moderate_impairment"
        }
    
    Returns:
        List of structured knowledge results
        
        Example return value:
        [
            {
                "source": "WHO AWaRe",
                "guideline_id": "who_aware:amoxicillin",
                "category": "Access",
                "evidence_level": "HIGH",
                "recommendation": "Amoxicillin is in WHO Access category",
                "citation": "WHO AWaRe 2023",
                "metadata": {"version": "2023", "year": 2023}
            }
        ]
    
    Guarantees:
    - Results are deterministic for same input
    - Results are ordered by relevance
    - Results include source attribution
    - Results include evidence level
    
    Behavior on missing results:
    - Return empty list (not None)
    - Log query for audit
    
    Raises:
    - ConnectionError if source is unavailable
    - TimeoutError if query exceeds timeout
    """
    raise NotImplementedError


@abstractmethod
def query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
    """Query the knowledge source with structured criteria.
    
    Alternative to search() for structured (non-text) queries.
    
    Parameters:
        criteria: Structured query parameters
        
        Example:
        {
            "drug": "amoxicillin",
            "indication": "pneumonia",
            "patient": {
                "age": 65,
                "renal_function": "moderate",
                "allergies": ["penicillin"]
            }
        }
    
    Returns:
        Structured knowledge result
        
        Example:
        {
            "source": "NICE",
            "guideline_id": "nice:pneumonia:primary",
            "category": "First-line",
            "evidence_level": "HIGH",
            "recommendation": "Use amoxicillin for community-acquired pneumonia",
            "contraindications": ["PCN allergy"],
            "citation": "NICE Respiratory Guidelines 2023",
            "metadata": {"guideline_version": "2023"}
        }
    
    Guarantees:
    - Result is deterministic for same input
    - Result matches the criteria exactly (no over-matching)
    - Result includes evidence level
    - Result includes citation
    
    Behavior on no match:
    - Return empty dict {} (not None)
    - Log query for audit
    
    Raises:
    - ConnectionError if source is unavailable
    - ValueError if criteria is invalid
    - TimeoutError if query exceeds timeout
    """
    raise NotImplementedError
```

### Domain and Version Methods

```python
@abstractmethod
def supported_domains(self) -> List[str]:
    """Return the clinical domains supported by this knowledge plugin.
    
    Used by AUTO routing to select appropriate plugins.
    
    Example domains:
    - "respiratory" (respiratory infections)
    - "gastrointestinal" (GI infections)
    - "urinary_tract" (UTI)
    - "wound" (surgical site infections)
    - "bloodstream" (bacteremia/sepsis)
    - "meningitis" (meningitis)
    - "general" (broad applicability, e.g., drug interactions)
    
    Returns:
        List of supported domain strings
        
        Example:
        ["respiratory", "gastrointestinal", "general"]
    
    Used by:
    - PluginRoutingPolicy._route_automatic()
    - Plugin discovery
    - Capability matching
    """
    raise NotImplementedError


@abstractmethod
def knowledge_version(self) -> str:
    """Return the version of the underlying knowledge data.
    
    Distinct from plugin_version (which tracks plugin code).
    
    Example:
    - Plugin version: "0.1.0" (plugin code version)
    - Knowledge version: "WHO AWaRe 2023" (data version)
    
    Returns:
        Version string of the knowledge base
        
        Examples:
        "WHO AWaRe 2023"
        "NICE Respiratory 2023"
        "IDSA Standards v2024"
    
    Used by:
    - Audit trail (what version of knowledge was used?)
    - Explicit version tracking
    - Evidence reproducibility
    """
    raise NotImplementedError
```

---

## Part 3: Complete Interface Contract

### Minimal Implementation

The minimal concrete Knowledge Plugin must implement:

```python
from app.plugins.base.knowledge_plugin import KnowledgePlugin
from app.plugins.base.plugin import PluginType, PluginMetadata, PluginHealth
from typing import Any, Dict, List, Optional
from datetime import datetime


class MyKnowledgePlugin(KnowledgePlugin):
    """Concrete Knowledge Plugin implementation."""
    
    def __init__(self):
        self._is_connected = False
    
    # Properties
    @property
    def plugin_id(self) -> str:
        return "my_knowledge_plugin"
    
    @property
    def plugin_name(self) -> str:
        return "My Knowledge Source"
    
    @property
    def plugin_version(self) -> str:
        return "0.1.0"
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.KNOWLEDGE
    
    @property
    def plugin_description(self) -> str:
        return "My custom knowledge plugin"
    
    @property
    def author(self) -> str:
        return "My Organization"
    
    @property
    def capabilities(self) -> List[str]:
        return ["search_guidelines", "provide_evidence"]
    
    @property
    def dependencies(self) -> List[str]:
        return []
    
    # Lifecycle methods (BasePlugin)
    def initialize(self) -> None:
        """Initialize at plugin load."""
        self._data = {}
    
    def shutdown(self) -> None:
        """Shutdown at plugin unload."""
        self._data = None
    
    def configure(self, configuration: Dict[str, Any]) -> None:
        """Configure with runtime parameters."""
        pass
    
    def validate(self) -> bool:
        """Validate readiness."""
        return True
    
    def metadata(self) -> PluginMetadata:
        """Return metadata."""
        return PluginMetadata(
            plugin_id=self.plugin_id,
            plugin_name=self.plugin_name,
            plugin_version=self.plugin_version,
            plugin_type=self.plugin_type,
            description=self.plugin_description,
            author=self.author,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
        )
    
    def health(self) -> PluginHealth:
        """Return health status."""
        return PluginHealth(
            healthy=self._is_connected,
            status="connected" if self._is_connected else "disconnected",
            message=None,
            timestamp=datetime.now(),
        )
    
    # Connection methods (KnowledgePlugin-specific)
    def connect(self) -> None:
        """Connect to knowledge source."""
        self._is_connected = True
    
    def disconnect(self) -> None:
        """Disconnect from knowledge source."""
        self._is_connected = False
    
    # Query methods (KnowledgePlugin-specific)
    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search knowledge source."""
        return [{
            "source": self.plugin_name,
            "guideline_id": "example:1",
            "recommendation": f"Evidence for: {query}",
            "citation": "My Knowledge Base v1.0"
        }]
    
    def query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Query with structured criteria."""
        return {
            "source": self.plugin_name,
            "guideline_id": "example:1",
            "recommendation": "Evidence based on criteria",
            "citation": "My Knowledge Base v1.0"
        }
    
    def supported_domains(self) -> List[str]:
        """Return supported domains."""
        return ["respiratory", "gastrointestinal"]
    
    def knowledge_version(self) -> str:
        """Return knowledge data version."""
        return "v1.0"
```

---

## Part 4: Integration Points

### How Workflow Manager Uses Knowledge Plugin Interface

```python
# Plugin discovery (from registry)
knowledge_plugins = [
    p for p in registry.plugins 
    if isinstance(p, KnowledgePlugin)
]

# Plugin routing (capability matching)
for plugin in knowledge_plugins:
    domains = plugin.supported_domains()
    if request_domain in domains:
        selected_plugins.append(plugin)

# Plugin execution
for plugin in selected_plugins:
    if plugin.validate():  # Check readiness
        plugin.connect()   # Establish connection
        try:
            result = plugin.search(query, filters)
            # Store in context
        finally:
            plugin.disconnect()  # Clean up

# Audit trail
metadata = plugin.metadata()
version = plugin.knowledge_version()
```

### How Explainability Engine Uses Knowledge Output

```python
# Knowledge outputs are in: context.knowledge_outputs
# Each output is: {"plugin_id": "...", "value": {...}}

for knowledge_output in context.knowledge_outputs:
    plugin_id = knowledge_output.get("plugin_id")
    value = knowledge_output.get("value")
    
    # Expects structured fields (optional):
    source = value.get("source")
    evidence_level = value.get("evidence_level")
    citation = value.get("citation")
    
    # Merges into explanation:
    explanation.evidence_drivers.append({
        "source": source,
        "weight": weight_by_evidence_level(evidence_level),
        "citation": citation,
        "text": value.get("recommendation")
    })
```

---

## Part 5: Output Contract Specification

### Recommended Output Format

Knowledge Plugins should return results following this structure:

```python
@dataclass
class KnowledgeResult:
    """Structured output format for Knowledge Plugins."""
    
    # Required fields
    source: str                                    # Plugin name
    guideline_id: str                              # Unique identifier
    recommendation: str                            # Clinical text
    citation: str                                  # Reference
    
    # Optional but recommended
    category: Optional[str] = None                 # Classification
    evidence_level: Optional[str] = None           # HIGH/MEDIUM/LOW
    contraindications: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Example - WHO AWaRe Knowledge Plugin:**

```python
def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Search WHO AWaRe by antibiotic name."""
    
    antibiotic = query.lower()
    result = self.database.query(
        f"SELECT category FROM who_aware WHERE drug = ?", 
        [antibiotic]
    )
    
    if not result:
        return []  # No match
    
    return [{
        "source": "WHO AWaRe",
        "guideline_id": f"who_aware:{antibiotic}",
        "category": result["category"],
        "evidence_level": "HIGH",  # WHO is authoritative
        "recommendation": f"{antibiotic} is in WHO AWaRe {result['category']} category",
        "citation": "WHO Access/Watch/Reserve classification (2023)",
        "contraindications": [],
        "metadata": {
            "version": "WHO AWaRe 2023",
            "year": 2023,
            "access_link": "https://www.who.int/publications/i/item/AWaRe"
        }
    }]
```

**Example - NICE Guidelines Knowledge Plugin:**

```python
def query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
    """Query NICE guidelines for treatment."""
    
    infection_type = criteria.get("infection")
    
    guideline = self.database.query(
        f"SELECT recommendation FROM nice_guidelines WHERE infection = ?",
        [infection_type]
    )
    
    if not guideline:
        return {}  # No match
    
    return {
        "source": "NICE Guidelines",
        "guideline_id": f"nice:{infection_type}:primary",
        "category": "First-line",
        "evidence_level": "HIGH",
        "recommendation": guideline["recommendation"],
        "citation": "NICE Respiratory and Infection Guidelines (2023)",
        "contraindications": [],
        "metadata": {
            "version": "NICE 2023",
            "guideline_code": guideline.get("code"),
            "nice_url": "https://nice.org.uk/..."
        }
    }
```

---

## Part 6: Error Handling Specification

### Exception Handling Expectations

Knowledge Plugins should handle errors gracefully:

```python
def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Search with error handling."""
    
    try:
        # Connection validation
        if not self._is_connected:
            raise ConnectionError("Knowledge source is not connected")
        
        # Query execution
        results = self.database.query(query)
        
        # Return empty list if no results (not an error)
        if not results:
            self.logger.debug(f"Query '{query}' returned no results")
            return []
        
        # Return structured results
        return [self._format_result(r) for r in results]
    
    except ConnectionError as exc:
        self.logger.error(f"Connection error in search: {exc}")
        raise
    except TimeoutError as exc:
        self.logger.error(f"Query timeout: {exc}")
        raise
    except ValueError as exc:
        self.logger.error(f"Invalid query: {exc}")
        raise
    except Exception as exc:
        self.logger.exception(f"Unexpected error in search: {exc}")
        raise
```

### Exceptions that Workflow Manager Expects to Catch

```python
try:
    result = plugin.search(query, filters)
except ConnectionError:
    # Knowledge source is unavailable
    # Workflow continues without this plugin
    pass
except TimeoutError:
    # Query took too long
    # Workflow continues without this plugin
    pass
except ValueError:
    # Invalid input
    # Workflow continues without this plugin
    pass
except Exception as exc:
    # Any other exception
    # Workflow continues without this plugin
    logger.error(f"Plugin {plugin.plugin_id} failed: {exc}")
    pass
```

---

## Part 7: Configuration Specification

Knowledge Plugins receive configuration in `configure()`:

### Example Configuration

```python
def configure(self, configuration: Dict[str, Any]) -> None:
    """Configure with runtime settings."""
    
    self.timeout_ms = configuration.get("timeout_ms", 5000)
    self.max_results = configuration.get("max_results", 100)
    self.api_key = configuration.get("api_key")
    self.cache_ttl_seconds = configuration.get("cache_ttl_seconds", 3600)
    
    # Validate configuration
    if not self.api_key:
        raise ValueError("api_key is required in configuration")
    
    # Apply settings
    self.database.set_timeout(self.timeout_ms)
    self.cache.set_ttl(self.cache_ttl_seconds)
```

### Configuration Injection in Plugin Manager

```python
# Plugin configuration (from .env or config file)
config = {
    "timeout_ms": 5000,
    "max_results": 100,
    "api_key": os.getenv("WHO_API_KEY"),
    "cache_ttl_seconds": 3600
}

# Inject into plugin
knowledge_plugin.configure(config)
```

---

## Summary of Interface Requirements

| Method | Status | Required? | Purpose |
|--------|--------|-----------|---------|
| `plugin_id` | ✅ | Yes | Unique identifier |
| `plugin_name` | ✅ | Yes | Human-readable name |
| `plugin_version` | ✅ | Yes | Plugin version |
| `plugin_type` | ✅ | Yes | Must be KNOWLEDGE |
| `plugin_description` | ✅ | Yes | Description |
| `author` | ✅ | Yes | Author/owner |
| `capabilities` | ✅ | Yes | Exposed capabilities |
| `dependencies` | ✅ | Yes | Dependencies |
| `initialize()` | ✅ | Yes | Startup initialization |
| `shutdown()` | ✅ | Yes | Cleanup |
| `configure()` | ✅ | Yes | Configuration injection |
| `validate()` | ✅ | Yes | Readiness check |
| `metadata()` | ✅ | Yes | Metadata structured form |
| `health()` | ✅ | Yes | Health status |
| `connect()` | ✅ | Yes | Knowledge source connection |
| `disconnect()` | ✅ | Yes | Connection cleanup |
| `search()` | ✅ | Yes | Text-based query |
| `query()` | ✅ | Yes | Structured query |
| `supported_domains()` | ✅ | Yes | Domain filtering |
| `knowledge_version()` | ✅ | Yes | Knowledge data version |

---

**End of Interface Report**

*All required methods are present and properly specified for Knowledge Plugin SDK v0.1.0*
