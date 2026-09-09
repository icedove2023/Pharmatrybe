# Plugin_SDK_Architecture.md

# PharmaTrybe Plugin SDK Architecture

**Version:** 1.0

**Status:** Core Backend Architecture

**Project:** PharmaTrybe Clinical Intelligence Platform

---

# 1. Purpose

The Plugin SDK provides the software architecture that allows developers to build, validate, register, deploy, and execute plugins within PharmaTrybe.

Unlike the Plugin Framework, which defines architectural principles, the Plugin SDK defines the actual software components that make plugin development possible.

The SDK serves as the bridge between external plugins and the PharmaTrybe platform.

---

# 2. Objectives

The Plugin SDK should provide:

* Standard plugin interfaces
* Plugin lifecycle management
* Automatic plugin discovery
* Dependency validation
* Configuration management
* Plugin health monitoring
* Workflow integration
* Decision Fusion integration
* Security isolation
* Version compatibility

---

# 3. SDK Architecture

```text
                       PharmaTrybe Core
                               │
                     Plugin Manager
                               │
        ┌──────────────┬──────────────┬──────────────┐
        │              │              │              │
 Plugin Registry   Plugin Loader   Plugin Validator  Plugin Health
        │              │              │              │
        └──────────────┴──────────────┴──────────────┘
                               │
                      Base Plugin SDK
                               │
    ┌──────────┬──────────┬──────────┬──────────┬──────────┐
    │          │          │          │          │
Prediction Knowledge  Risk    Rules  Integration
 Plugin     Plugin   Plugin   Plugin    Plugin
```

---

# 4. SDK Directory Structure

```text
apps/
└── api/
    └── app/
        └── plugins/
            ├── base/
            │   ├── plugin.py
            │   ├── prediction_plugin.py
            │   ├── knowledge_plugin.py
            │   ├── risk_plugin.py
            │   ├── rules_plugin.py
            │   ├── reporting_plugin.py
            │   └── integration_plugin.py
            │
            ├── manager/
            │   ├── plugin_manager.py
            │   ├── plugin_loader.py
            │   ├── plugin_registry.py
            │   ├── plugin_validator.py
            │   ├── plugin_health.py
            │   └── workflow_manager.py
            │
            ├── contracts/
            │   ├── prediction.py
            │   ├── knowledge.py
            │   ├── workflow.py
            │   ├── explainability.py
            │   ├── risk.py
            │   └── rules.py
            │
            ├── discovery/
            │
            ├── exceptions/
            │
            ├── models/
            │
            └── utils/
```

---

# 5. Core SDK Components

The Plugin SDK consists of six core services.

## Base Plugin

Defines the minimum interface every plugin must implement.

Responsibilities:

* Lifecycle
* Configuration
* Metadata
* Health
* Validation

---

## Plugin Loader

Responsible for loading plugins.

Responsibilities:

* Locate plugin
* Read manifest
* Load classes
* Resolve dependencies
* Initialize plugin

---

## Plugin Registry

Acts as the central inventory.

Responsibilities:

* Register plugins
* Store metadata
* Store versions
* Store capabilities
* Store categories

---

## Plugin Validator

Ensures plugin compliance.

Validation includes:

* Manifest validation
* Interface validation
* Dependency validation
* Version validation
* Configuration validation

---

## Plugin Health

Monitors plugin availability.

Checks:

* Internal status
* External connections
* Deployment artifacts
* Response time

---

## Workflow Manager

Responsible for workflow execution.

Responsibilities:

* Load workflow
* Resolve plugins
* Configure Decision Fusion
* Execute plugin chain

---

# 6. Base Plugin

Every plugin inherits from BasePlugin.

```python
class BasePlugin:

    initialize()

    shutdown()

    configure()

    validate()

    metadata()

    health()
```

No plugin bypasses this interface.

---

# 7. Specialized Plugin Classes

The SDK provides specialized base classes.

```text
BasePlugin

│

├── PredictionPlugin

├── KnowledgePlugin

├── RiskPlugin

├── RulesPlugin

├── ReportingPlugin

└── IntegrationPlugin
```

Developers inherit only the class they require.

---

# 8. Prediction Plugin SDK

Prediction plugins support two deployment models.

## Artifact Prediction

```text
Developer

↓

PredictionPlugin

↓

Artifact Loader

↓

Model

↓

Prediction
```

---

## API Prediction

```text
Developer

↓

PredictionPlugin

↓

REST Client

↓

Hospital API

↓

Prediction
```

The Decision Fusion Engine cannot distinguish between these deployment methods.

---

# 9. Knowledge Plugin SDK

Knowledge plugins expose structured knowledge.

Supported sources include:

* PostgreSQL
* SQLite
* Supabase
* MongoDB
* REST APIs
* GraphQL

Knowledge plugins never parse documents.

Document processing occurs outside PharmaTrybe.

---

# 10. Plugin Manifest

Every plugin must include:

```text
plugin.yaml
```

The manifest defines:

* Plugin ID
* Name
* Version
* Category
* Capabilities
* Dependencies
* Configuration
* Author
* Deployment type

---

# 11. Plugin Discovery

Plugins are automatically discovered.

Process:

```text
Scan Plugins

↓

Read Manifest

↓

Validate

↓

Register

↓

Initialize

↓

Ready
```

No manual registration is required.

---

# 12. Plugin Registration

The registry stores:

* Plugin ID
* Category
* Version
* Author
* Capabilities
* Workflow compatibility
* Health status
* Configuration

The registry is the authoritative source of installed plugins.

---

# 13. Plugin Loading

The Plugin Loader performs:

```text
Read Manifest

↓

Validate

↓

Resolve Dependencies

↓

Load Classes

↓

Instantiate Plugin

↓

Initialize

↓

Health Check

↓

Register
```

---

# 14. Configuration System

Each plugin owns its configuration.

Example:

```yaml
timeout: 30

retry: 3

api_key: ****

endpoint: ...
```

The platform never stores plugin-specific business configuration.

---

# 15. Workflow Integration

Plugins never decide when they execute.

Instead:

```text
Workflow

↓

Workflow Manager

↓

Plugin Manager

↓

Selected Plugins

↓

Decision Fusion
```

A workflow determines:

* Active prediction plugins
* Active knowledge plugins
* Active rules
* Active risk engines

---

# 16. Decision Fusion Integration

Decision Fusion requests evidence.

Plugins provide evidence.

Example:

```text
Prediction Plugins

↓

Prediction Evidence

Knowledge Plugins

↓

Knowledge Evidence

Risk Plugins

↓

Risk Evidence

Rules Plugins

↓

Policy Evidence

↓

Decision Fusion

↓

Clinical Recommendation
```

Plugins never generate recommendations.

---

# 17. Explainability Integration

Prediction plugins should expose:

* Feature names
* Probability
* Confidence
* SHAP compatibility

Knowledge plugins should expose:

* Source
* Citation
* Guideline version

Decision Fusion combines all explainability sources into a unified explanation.

---

# 18. Plugin Lifecycle

```text
Develop

↓

Package

↓

Install

↓

Discover

↓

Validate

↓

Register

↓

Configure

↓

Initialize

↓

Execute

↓

Monitor

↓

Update

↓

Disable

↓

Remove
```

---

# 19. Plugin Communication

Plugins never communicate directly.

All communication passes through:

```text
Plugin

↓

Plugin Manager

↓

Platform Services

↓

Decision Fusion
```

This prevents coupling between plugins.

---

# 20. Error Isolation

Plugin failures remain isolated.

If one plugin fails:

```text
Prediction Plugin A

×

↓

Plugin Manager

↓

Continue

↓

Decision Fusion
```

The platform should continue operating whenever possible.

---

# 21. Developer Workflow

Developers creating plugins should follow:

```text
Create Plugin

↓

Implement SDK Interface

↓

Create Manifest

↓

Add Tests

↓

Validate

↓

Install

↓

Configure Workflow

↓

Activate
```

---

# 22. Example Development Flow

## SOAR

```text
PredictionPlugin

↓

Artifact Loader

↓

SOAR Runtime

↓

Prediction
```

---

## ARMD

```text
PredictionPlugin

↓

REST Client

↓

ARMD API

↓

Prediction
```

Both appear identical to Decision Fusion.

---

## WHO

```text
KnowledgePlugin

↓

Supabase

↓

Structured Knowledge

↓

Evidence
```

---

## Hospital Guideline

```text
KnowledgePlugin

↓

Hospital Database

↓

Evidence
```

---

# 23. Future SDK Extensions

The SDK should support future plugin types without architectural changes.

Potential additions include:

* Imaging AI
* Pharmacogenomics
* Clinical NLP
* Digital Therapeutics
* Public Health Surveillance
* Laboratory Automation
* Drug Interaction Engines

---

# 24. Architectural Principle

The Plugin SDK exists to ensure that every extension integrates through a single, standardized mechanism.

Whether the extension is:

* a local artifact model such as SOAR,
* an external API such as ARMD,
* a hospital-developed prediction model,
* a WHO knowledge database,
* a local antimicrobial guideline,
* a hospital stewardship policy,
* or a future clinical intelligence component,

the Plugin Manager treats them uniformly.

This architecture allows PharmaTrybe to evolve into a true Clinical Intelligence Platform where new capabilities can be introduced without modifying the platform core, while preserving the integrity of the Decision Fusion Engine, Explainability Engine, Clinical Rules Engine, Clinical Response Engine, and Audit Engine.
