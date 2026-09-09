# WHO Knowledge Plugin — API Reference

**Status:** ✅ COMPLETE

**Version:** 0.1.0

---

## Quick Reference

### Plugin Identity

```python
plugin_id: str = "who_knowledge"
plugin_name: str = "WHO Knowledge Base"
plugin_version: str = "0.1.0"
plugin_type: PluginType = PluginType.KNOWLEDGE
```

### Instantiation

```python
from sqlalchemy.orm import Session
from app.plugins.knowledge.who_knowledge_plugin import WHOKnowledgePlugin

# Create plugin with database session
db_session: Session = ...  # From your session factory
plugin = WHOKnowledgePlugin(db_session=db_session)

# Initialize
plugin.initialize()

# Connect
plugin.connect()

# Now ready to use
assert plugin.validate()
```

---

## Properties

### `plugin_id` → `str`

Unique identifier for the plugin in registry.

**Value:** `"who_knowledge"`

**Usage:** Registry lookups, routing, audit trails

```python
plugin_id = plugin.plugin_id
# "who_knowledge"
```

---

### `plugin_name` → `str`

Human-readable name for UI and logging.

**Value:** `"WHO Knowledge Base"`

**Usage:** Display, logging, documentation

```python
name = plugin.plugin_name
# "WHO Knowledge Base"
```

---

### `plugin_version` → `str`

Code version of the plugin (not data version).

**Value:** `"0.1.0"`

**Semantic Versioning:** MAJOR.MINOR.PATCH

**Usage:** Compatibility checks, audit trails

```python
version = plugin.plugin_version
# "0.1.0"
```

---

### `plugin_type` → `PluginType`

Plugin category type.

**Value:** `PluginType.KNOWLEDGE`

**Usage:** Routing decisions, type filtering

```python
if plugin.plugin_type == PluginType.KNOWLEDGE:
    # Route to knowledge plugins
```

---

### `plugin_description` → `str`

Long-form description.

**Value:** `"WHO respiratory infection clinical guidelines and antimicrobial stewardship evidence"`

---

### `author` → `str`

Plugin author/owner for accountability.

**Value:** `"WHO / PharmaTrybe Team"`

---

### `capabilities` → `List[str]`

Capabilities exposed to routing and discovery.

**Value:** 
```python
[
    "disease_guidelines",
    "antibiotic_classification",
    "antimicrobial_stewardship",
    "diagnostic_guidance",
    "treatment_recommendations",
    "monitoring_guidance",
    "follow_up_guidance",
    "evidence_retrieval",
]
```

**Usage:** AUTO routing capability matching

```python
if "disease_guidelines" in plugin.capabilities:
    # Plugin can provide disease guidelines
```

---

### `dependencies` → `List[str]`

External dependencies required.

**Value:**
```python
[
    "python3.9+",
    "sqlalchemy",
    "postgresql",
]
```

---

## Lifecycle Methods

### `initialize()` → `None`

Initialize plugin at startup.

**Purpose:** Set up internal state, logging, timing

**Called by:** Plugin Registry during plugin load

**Does NOT:** Connect to database (see `connect()`)

**Example:**
```python
plugin.initialize()
# Plugin is ready for configure() and connect()
```

---

### `shutdown()` → `None`

Shutdown plugin at unload.

**Purpose:** Clean up resources, close connections

**Called by:** Plugin Registry during plugin unload

**Does NOT:** Raise exceptions (graceful only)

**Example:**
```python
plugin.shutdown()
# Plugin no longer usable
```

---

### `configure(configuration: Dict[str, Any])` → `None`

Configure plugin with runtime parameters.

**Parameters:**
- `configuration`: Config dictionary (currently unused for WHO)

**Raises:**
- `ValueError` if configuration is invalid

**Example:**
```python
plugin.configure({})
# WHO plugin has no special configuration
```

---

### `validate()` → `bool`

Validate plugin readiness.

**Returns:**
- `True` if ready to handle requests
- `False` if not ready (not connected, error state)

**Usage:** Health checks, pre-request validation

**Example:**
```python
if plugin.validate():
    results = plugin.search("pneumonia")
else:
    # Plugin not ready
    pass
```

---

### `metadata()` → `PluginMetadata`

Return structured plugin metadata.

**Returns:** `PluginMetadata` dataclass with all identification info

**Example:**
```python
metadata = plugin.metadata()
print(metadata.plugin_id)    # "who_knowledge"
print(metadata.plugin_name)  # "WHO Knowledge Base"
print(metadata.capabilities) # [...8 capabilities...]
```

---

### `health()` → `PluginHealth`

Return health status.

**Returns:** `PluginHealth` dataclass with:
- `healthy: bool` - Is plugin operational?
- `status: str` - Status description ("connected", "disconnected")
- `message: Optional[str]` - Error message if unhealthy
- `timestamp: datetime` - When checked

**Example:**
```python
health = plugin.health()
if health.healthy:
    print("WHO plugin is healthy")
else:
    print(f"WHO plugin issue: {health.message}")
```

---

## Connection Methods

### `connect()` → `None`

Connect to the WHO knowledge source.

**Purpose:** Initialize repository and provider instances

**Called by:** Workflow Manager before execution

**Raises:**
- `ConnectionError` if connection fails (no session, DB error, etc.)

**Example:**
```python
try:
    plugin.connect()
    print("Connected to WHO knowledge base")
except ConnectionError as e:
    print(f"Connection failed: {e}")
```

---

### `disconnect()` → `None`

Disconnect from WHO knowledge source.

**Purpose:** Clean up repository and provider instances

**Called by:** Workflow Manager after execution or on shutdown

**Does NOT:** Raise exceptions

**Example:**
```python
plugin.disconnect()
# Plugin can no longer answer queries
```

---

## Query Methods

### `search(query: str, filters: Optional[Dict[str, Any]] = None)` → `List[Dict[str, Any]]`

Search WHO knowledge base with text query.

**Parameters:**
- `query` (str): Search text
  - Examples: "pneumonia", "amoxicillin", "respiratory infection"
  - Empty string returns empty list
- `filters` (dict, optional): Filter criteria (reserved for future use)

**Returns:** List of structured `WHOKnowledgeResult` dicts

**Raises:**
- `ConnectionError` if knowledge source unavailable

**Result Fields:** See `WHOKnowledgeResult` below

**Example:**
```python
# Search for disease
results = plugin.search("pneumonia")
for result in results:
    print(f"Found: {result['entity_name']}")
    print(f"  Type: {result['result_type']}")
    print(f"  Evidence Level: {result['evidence_level']}")
```

---

### `query(criteria: Dict[str, Any])` → `Dict[str, Any]`

Query WHO knowledge with structured criteria.

**Parameters:**
- `criteria` (dict): Query parameters

**Supported Criteria:**

**By Disease ID:**
```python
criteria = {"disease_id": "d_123"}
result = plugin.query(criteria)
# Returns complete disease guideline
```

**By Drug Name:**
```python
criteria = {"drug_name": "Amoxicillin"}
result = plugin.query(criteria)
# Returns drug classification and guidelines
```

**Returns:** Single structured `WHOKnowledgeResult` dict, or empty dict if no match

**Raises:**
- `ConnectionError` if knowledge source unavailable
- `ValueError` if criteria invalid

**Example:**
```python
# Query by disease
result = plugin.query({"disease_id": "pneumonia_001"})

if result:
    print(f"Disease: {result['entity_name']}")
    print(f"Recommendation: {result['clinical_recommendation']}")
else:
    print("Disease not found")
```

---

## Information Retrieval Methods

### `supported_domains()` → `List[str]`

Return supported clinical domains.

**Returns:** List of domain strings

**Value:**
```python
[
    "respiratory",
    "gastrointestinal",
    "urinary_tract",
    "wound",
    "bloodstream",
    "meningitis",
    "general",
]
```

**Usage:** Routing policy domain matching

```python
if "respiratory" in plugin.supported_domains():
    # Plugin can handle respiratory cases
```

---

### `knowledge_version()` → `str`

Return WHO knowledge data version.

**Returns:** Version string (not code version)

**Value:** `"WHO 2023"`

**Usage:** Audit trail, result attribution

```python
version = plugin.knowledge_version()
# "WHO 2023"
```

---

### `explain(entity_id: str, entity_type: str = "disease")` → `Dict[str, Any]`

Generate explainable evidence for an entity.

**Parameters:**
- `entity_id` (str): ID of entity to explain
- `entity_type` (str): "disease", "drug", or "recommendation"

**Returns:** Dictionary with explainable information

**Return Fields:**
- `source` (str): "WHO"
- `entity_id` (str): The queried entity
- `entity_name` (str): Display name
- `entity_type` (str): Type (disease, drug, etc.)
- `evidence` (list): List of evidence statements
- `recommendations` (list): Associated recommendations
- `timestamp` (str): ISO8601 timestamp

**Raises:**
- `ConnectionError` if knowledge source unavailable

**Example:**
```python
explanation = plugin.explain("d_pneumonia", entity_type="disease")

print(f"Explaining: {explanation['entity_name']}")
print(f"Evidence statements: {len(explanation['evidence'])}")
print(f"Recommendations: {len(explanation['recommendations'])}")

for evidence in explanation['evidence']:
    print(f"  - {evidence['text']}")
```

---

## Data Structures

### `WHOKnowledgeResult`

Structured output from WHO plugin queries.

**Fields:**

```python
@dataclass
class WHOKnowledgeResult:
    # Attribution
    source: str = "WHO"
    plugin_version: str = ""
    knowledge_version: str = ""
    
    # Entity Classification
    result_type: str = ""  # "disease", "drug", "recommendation"
    
    # Entity Information
    entity_id: str = ""
    entity_name: str = ""
    entity_description: str = ""
    
    # Clinical Classification
    guideline_category: Optional[str] = None  # "Access"/"Watch"/"Reserve"
    clinical_recommendation: str = ""
    evidence_level: str = "MEDIUM"  # "HIGH", "MEDIUM", "LOW"
    
    # Citation and Metadata
    citation: str = "WHO Guidelines"
    source_version: str = ""
    metadata: Dict[str, Any] = {}
```

**Serialization:**
```python
result = WHOKnowledgeResult(...)
result_dict = result.to_dict()  # Convert to Dict[str, Any]
```

**Example:**
```python
{
    "source": "WHO",
    "plugin_version": "0.1.0",
    "knowledge_version": "WHO 2023",
    "result_type": "disease",
    "entity_id": "d_pneumonia",
    "entity_name": "Community-Acquired Pneumonia",
    "entity_description": "Lower respiratory tract infection...",
    "guideline_category": None,
    "clinical_recommendation": "Follow WHO treatment guidelines",
    "evidence_level": "HIGH",
    "citation": "WHO Guidelines - Community-Acquired Pneumonia",
    "source_version": "WHO 2023",
    "metadata": {
        "care_level": "primary",
        "chapter": 5,
        "disease_id": "d_pneumonia"
    }
}
```

---

## Execution Flow in Workflow Manager

### Complete Request-Response Cycle

```python
# 1. Workflow Manager routes request
request = ClinicalDecisionRequest(
    patient_id="p123",
    payload={"query": "pneumonia"},
    context={"domain": "respiratory"},
    execution_mode="AUTO"
)

# 2. Routing Policy selects WHO plugin
# (domain = "respiratory" matches plugin.supported_domains())
selected_plugins = [who_knowledge_plugin]

# 3. Workflow Manager executes
result = plugin.search("pneumonia", filters={})

# 4. Aggregates into context
context.knowledge_outputs.append({
    "plugin_id": "who_knowledge",
    "plugin_name": "WHO Knowledge Base",
    "value": result  # List[Dict[str, Any]]
})

# 5. Pipeline uses for evidence
# (not for recommendations)

# 6. Explainability Engine accesses
for knowledge_output in context.knowledge_outputs:
    plugin_id = knowledge_output["plugin_id"]  # "who_knowledge"
    value = knowledge_output["value"]  # The result
    
    # Extract key fields for explanation
    source = value[0]["source"]  # "WHO"
    citation = value[0]["citation"]
    evidence_level = value[0]["evidence_level"]
```

---

## Error Handling

### Exception Handling

```python
try:
    results = plugin.search("query")
except ConnectionError as e:
    # Knowledge source unavailable
    # Workflow Manager catches and continues
    logger.error(f"WHO plugin connection error: {e}")
except ValueError as e:
    # Invalid input
    logger.error(f"WHO plugin validation error: {e}")
except Exception as e:
    # Unexpected error
    logger.exception(f"WHO plugin error: {e}")
```

### Graceful Degradation

```python
# Empty query
results = plugin.search("")  # Returns []

# Invalid criteria
result = plugin.query({})  # Returns {}

# Missing entity
result = plugin.query({"disease_id": "nonexistent"})  # Returns {}

# Not connected
try:
    plugin.search("query")  # Raises ConnectionError
except ConnectionError:
    # Handle gracefully
    pass
```

---

## Usage Examples

### Example 1: Search for Disease

```python
from app.plugins.knowledge.who_knowledge_plugin import WHOKnowledgePlugin

# Create and initialize
plugin = WHOKnowledgePlugin(db_session=session)
plugin.initialize()
plugin.connect()

# Search
if plugin.validate():
    results = plugin.search("pneumonia")
    
    for result in results:
        print(f"Found: {result['entity_name']}")
        print(f"Level: {result['evidence_level']}")
        print(f"Recommendation: {result['clinical_recommendation']}")
```

### Example 2: Query Drug Classification

```python
# Query drug by name
result = plugin.query({"drug_name": "Amoxicillin"})

if result:
    print(f"Drug: {result['entity_name']}")
    print(f"WHO Category: {result['guideline_category']}")
    print(f"Citation: {result['citation']}")
```

### Example 3: Get Explainable Evidence

```python
# Explain a disease guideline
explanation = plugin.explain("d_pneumonia", entity_type="disease")

print(f"Disease: {explanation['entity_name']}")
print(f"Evidence sources: {len(explanation['evidence'])}")

for evidence in explanation['evidence']:
    print(f"  - {evidence['source']}: {evidence['text']}")
```

### Example 4: Integration with Workflow

```python
from app.plugins.manager.workflow_manager import WorkflowManager, ClinicalDecisionRequest
from app.plugins.manager.plugin_registry import PluginRegistry

# Register plugin
registry = PluginRegistry()
registry.register("who_knowledge", plugin)

# Create workflow request
request = ClinicalDecisionRequest(
    patient_id="p123",
    payload={"query": "respiratory infection treatment"},
    context={"domain": "respiratory"},
    execution_mode="AUTO"
)

# Execute
manager = WorkflowManager(registry)
results = manager.execute(request)

# Process WHO results
for result in results:
    if result.plugin_id == "who_knowledge" and result.success:
        knowledge = result.result  # List[Dict]
        print(f"WHO evidence: {len(knowledge)} items")
```

---

## Troubleshooting

### Plugin Not Connecting

```python
if not plugin.validate():
    health = plugin.health()
    print(f"Status: {health.status}")
    print(f"Message: {health.message}")
    
    # Likely causes:
    # - Database session not provided
    # - Database connection failed
    # - Repository initialization failed
```

### Empty Results from Search

```python
results = plugin.search("query")

if not results:
    # Causes:
    # 1. Query doesn't match any diseases or drugs
    # 2. Database is empty (unlikely with WHO data)
    # 3. Connection lost
    
    if plugin.validate():
        # Connection is fine, just no matches
        pass
    else:
        # Connection issue
        pass
```

### Plugin Not Selected by Router

```python
# Check if domain is supported
if "respiratory" not in plugin.supported_domains():
    # Plugin won't be selected for respiratory domain

# Check if routing mode is correct
# - AUTO: Requires domain support
# - KNOWLEDGE_ONLY: Always selects all knowledge plugins
# - HYBRID: Selects WHO + predictions
# - USER_SELECTED: Only if explicitly requested
```

---

## API Versioning

**Plugin Code Version:** `0.1.0`

**WHO Knowledge Version:** `WHO 2023`

**Minimum Platform Version:** `5.0.0`

**SDK Version:** `0.1.0` (Knowledge Plugin SDK)

---

**End of API Reference**

*WHO Knowledge Plugin provides WHO clinical knowledge through the standardized Knowledge Plugin interface.*
