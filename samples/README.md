# 📚 Sample Creation Strategy for CDM-TAF Ontology

## 📋 Overview

The **CDM-TAF (Common Data Model - Telematics Application Framework)** ontology is a modular, domain-specific ontology designed for railway telematics and operational management. The ontology comprises **18-20 distinct modules**, each representing a specific aspect of railway operations, from foundational concepts like time and location to complex operational states and messaging.

This document outlines a strategic, **module-by-module programmatic generation approach** for creating comprehensive sample datasets that demonstrate the ontology's capabilities while maintaining modularity, reusability, and extensibility.

---

## 🎯 Recommended Approach: Module-by-Module Programmatic Generation

The recommended strategy prioritizes a **systematic, tier-based approach** that:

1. **Starts with foundational modules** to establish core building blocks
2. **Progressively builds complexity** by layering dependent modules
3. **Uses programmatic generation** (Python) for Tier 2+ to ensure consistency and scalability
4. **Validates samples** against JSON-LD schemas to ensure compliance
5. **Provides reusable templates and patterns** for each module type

### Why This Approach?

- ✅ **Modularity**: Each module can be developed, tested, and validated independently
- ✅ **Scalability**: Programmatic generation handles complex, interconnected data efficiently
- ✅ **Maintainability**: Changes to one module don't cascade unnecessarily
- ✅ **Validation**: Schema-based validation ensures correctness at each step
- ✅ **Documentation**: Samples serve as living documentation for each module

---

## 🏗️ Module Categorization: 5-Tier Structure

### **Tier 1: Foundation Modules** 🧱
*Core primitives with minimal dependencies*

- **Module 90**: Time
- **Module 99**: Varia (Miscellaneous utilities)
- **Module 03**: Operational Location
- **Module 01/01a**: Operational Entities
- **Module 12**: Versioned Description

### **Tier 2: Core Entity Modules** 🚂
*Primary domain entities built on Tier 1*

- **Module 04**: Train
- **Module 05**: Wagon
- **Module 06**: ITU (Intermodal Transport Unit)

### **Tier 3: Infrastructure Modules** 🛤️
*Physical and logical infrastructure*

- **Module 07**: Track
- **Module 08**: Facility

### **Tier 4: Role & Relationship Modules** 🔗
*Roles, relationships, and compositions*

- **Module 09**: Traction Role
- **Module 10**: Load Role
- **Module 11**: Operational Role

### **Tier 5: Operations & Scheduling Modules** 📅
*Operational processes and schedules*

- **Module 02/02a**: Train Run & Train Servicing
- **Module 12a/12b/12c**: Journey, Journey Schedule, Journey Schedule Properties

### **Tier 6: State Management & Communication** 📡
*States, messages, and external data*

- **Module 13/13a/13b/13c**: Operational State/Situation
- **Module 14**: Message
- **Module 15**: Image
- **Module 20**: RID (Reference & Identification Data)

---

## 🧱 Foundation Modules (Tier 1): Detailed Breakdown

### 1. **Module 90: Time** ⏰

**Purpose**: Defines temporal concepts and time-related properties

**Key Concepts**:
- Time instants and intervals
- Scheduled vs. actual times
- Time zones and UTC handling
- Temporal relationships

**Sample Focus**:
- Simple timestamp examples
- Time interval representations
- Scheduled time vs. actual time comparisons

**Dependencies**: None (pure foundation)

---

### 2. **Module 99: Varia** 🔧

**Purpose**: Miscellaneous utilities, identifiers, and cross-cutting concerns

**Key Concepts**:
- Identifiers and codes
- Enumerations
- Units of measure
- Common utilities

**Sample Focus**:
- Standard identifier patterns
- Code list examples
- Unit conversions

**Dependencies**: None

---

### 3. **Module 03: Operational Location** 📍

**Purpose**: Defines locations relevant to railway operations

**Key Concepts**:
- Stations
- Junctions
- Yards
- Geolocation data
- Location hierarchies

**Sample Focus**:
- Major station examples
- Location with coordinates
- Parent-child location relationships

**Dependencies**: Module 99 (for identifiers)

---

### 4. **Module 01/01a: Operational Entities** 🏢

**Purpose**: Defines organizational entities involved in operations

**Key Concepts**:
- Railway undertakings (RUs)
- Infrastructure managers (IMs)
- Terminal operators
- Entity relationships and hierarchies

**Sample Focus**:
- Sample RUs and IMs
- Entity details and contact information
- Organizational structures

**Dependencies**: Module 99 (for identifiers)

---

### 5. **Module 12: Versioned Description** 📝

**Purpose**: Manages versioning and descriptions for evolving entities

**Key Concepts**:
- Version control
- Temporal validity
- Description metadata
- Change tracking

**Sample Focus**:
- Versioned entity examples
- Valid-from/valid-to examples
- Version history chains

**Dependencies**: Module 90 (Time)

---

## 📅 Implementation Phases: Week-by-Week Breakdown

### **Week 1-2: Setup & Tier 1 Foundation** 🎬

**Objectives**:
- Set up development environment
- Implement Tier 1 modules (Modules 90, 99, 03, 01/01a, 12)
- Create validation framework

**Deliverables**:
- Working Python generation scripts for foundational modules
- 5-10 validated samples per module
- Schema validation tests passing

---

### **Week 3-4: Tier 2 Core Entities** 🚂

**Objectives**:
- Implement Train, Wagon, ITU modules
- Link entities to Tier 1 foundations

**Deliverables**:
- Train composition examples
- Wagon fleet samples
- ITU container examples
- Cross-module validation tests

---

### **Week 5-6: Tier 3 Infrastructure** 🛤️

**Objectives**:
- Implement Track and Facility modules
- Create infrastructure topology samples

**Deliverables**:
- Track layout examples
- Facility (depot, terminal) samples
- Infrastructure-location linkages

---

### **Week 7-8: Tier 4 Roles & Tier 5 Operations** 🔗📅

**Objectives**:
- Implement Role modules (09, 10, 11)
- Implement Train Run and Journey modules

**Deliverables**:
- Role assignment examples
- Complete train run scenarios
- Journey schedule samples

---

### **Week 9-10: Tier 6 States & Communication** 📡

**Objectives**:
- Implement State Management modules
- Implement Message and Image modules

**Deliverables**:
- Operational state samples
- Message exchange examples
- Complete end-to-end scenarios

---

### **Week 11-12: Integration & Refinement** 🎯

**Objectives**:
- Create complex multi-module scenarios
- Comprehensive validation
- Documentation and guides

**Deliverables**:
- 3-5 complete operational scenarios
- Full documentation
- Sample catalog and index

---

## 🛠️ Tool Stack Recommendations

### **For Tier 1: JSON Editor with Schema Validation** ✏️

**Recommended Tools**:
- **VS Code** with JSON Schema extension
- **JetBrains IDEs** (PyCharm, IntelliJ) with JSON validation
- **Online validators**: [jsonschemavalidator.net](https://www.jsonschemavalidator.net/)

**Workflow**:
```
1. Load schema: Schemas/tafp5_schema.json
2. Create sample JSON-LD file
3. Validate against schema in real-time
4. Test with sample data
5. Commit validated samples
```

**Advantages**:
- Visual feedback
- Immediate validation
- Good for understanding schema structure
- Low learning curve

---

### **For Tier 2+: Python Programmatic Generation** 🐍

**Recommended Libraries**:

```python
# Core RDF libraries
rdflib          # RDF graph manipulation
pyld            # JSON-LD processing

# Validation & Testing
jsonschema      # Schema validation
pytest          # Testing framework

# Data generation
faker           # Generate realistic test data
```

**Example Generation Script Structure**:

```python
#!/usr/bin/env python3
"""
Generate samples for Module 04: Train
"""
from rdflib import Graph, Namespace, Literal, URIRef
from pyld import jsonld
import json

# Define namespaces
TAFP5 = Namespace("http://data.europa.eu/949/ontology/tafp5#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

def create_train_sample(train_id, operator_id):
    """Generate a sample train entity"""
    g = Graph()
    
    # Create train entity
    train_uri = URIRef(f"http://example.org/trains/{train_id}")
    g.add((train_uri, RDF.type, TAFP5.Train))
    g.add((train_uri, TAFP5.trainIdentifier, Literal(train_id)))
    g.add((train_uri, TAFP5.operator, URIRef(operator_id)))
    
    # Convert to JSON-LD
    jsonld_data = json.loads(g.serialize(format='json-ld'))
    
    return jsonld_data

def validate_sample(sample_data, schema_path):
    """Validate sample against JSON schema"""
    with open(schema_path) as f:
        schema = json.load(f)
    
    jsonschema.validate(instance=sample_data, schema=schema)
    return True

# Generate samples
if __name__ == "__main__":
    sample = create_train_sample("TRAIN001", "http://example.org/operators/OP001")
    
    # Validate
    validate_sample(sample, "../Schemas/tafp5_schema.json")
    
    # Save
    with open("train_001.jsonld", "w") as f:
        json.dump(sample, f, indent=2)
```

**Advantages**:
- Automated generation of complex samples
- Consistent patterns across modules
- Easy to generate large datasets
- Programmatic validation
- Reusable templates and functions

---

## 📂 Sample Organization Structure

```
samples/
├── README.md                          # This file
├── schemas/                           # Schema references (symlinks or copies)
│   ├── composite_schema.json
│   └── tafp5_schema.json
│
├── tier1_foundation/                  # Tier 1: Foundation modules
│   ├── module_90_time/
│   │   ├── time_instant_01.jsonld
│   │   ├── time_interval_01.jsonld
│   │   └── scheduled_vs_actual.jsonld
│   ├── module_99_varia/
│   │   ├── identifier_patterns.jsonld
│   │   └── code_lists.jsonld
│   ├── module_03_location/
│   │   ├── station_paris_nord.jsonld
│   │   ├── junction_example.jsonld
│   │   └── location_hierarchy.jsonld
│   ├── module_01_entities/
│   │   ├── railway_undertaking_01.jsonld
│   │   └── infrastructure_manager_01.jsonld
│   └── module_12_versioned/
│       ├── versioned_entity_01.jsonld
│       └── version_history.jsonld
│
├── tier2_core_entities/               # Tier 2: Core entities
│   ├── module_04_train/
│   ├── module_05_wagon/
│   └── module_06_itu/
│
├── tier3_infrastructure/              # Tier 3: Infrastructure
│   ├── module_07_track/
│   └── module_08_facility/
│
├── tier4_roles/                       # Tier 4: Roles
│   ├── module_09_traction_role/
│   ├── module_10_load_role/
│   └── module_11_operational_role/
│
├── tier5_operations/                  # Tier 5: Operations
│   ├── module_02_train_run/
│   └── module_12_journey/
│
├── tier6_state_communication/         # Tier 6: States & Messages
│   ├── module_13_operational_state/
│   ├── module_14_message/
│   ├── module_15_image/
│   └── module_20_rid/
│
├── scenarios/                         # Complete end-to-end scenarios
│   ├── scenario_01_freight_journey/
│   ├── scenario_02_passenger_service/
│   └── scenario_03_terminal_operations/
│
└── scripts/                           # Generation scripts
    ├── generate_tier1.py
    ├── generate_tier2.py
    ├── validate_all.py
    └── utils/
        ├── rdf_helpers.py
        └── validators.py
```

---

## 🧪 Prototype Approach: Testing with One Simple Module

### Step 1: Choose the Simplest Module

**Start with Module 90: Time** - It has no dependencies and clear, well-defined concepts.

### Step 2: Manual Sample Creation

Create a simple JSON-LD sample manually:

```json
{
  "@context": {
    "tafp5": "http://data.europa.eu/949/ontology/tafp5#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@type": "tafp5:TimeInstant",
  "@id": "http://example.org/time/instant/001",
  "tafp5:timestamp": {
    "@type": "xsd:dateTime",
    "@value": "2024-11-25T10:30:00Z"
  },
  "tafp5:timezone": "UTC"
}
```

### Step 3: Validate Against Schema

```bash
# Using Python
python scripts/validate_sample.py \
  --sample samples/tier1_foundation/module_90_time/time_instant_01.jsonld \
  --schema Schemas/tafp5_schema.json
```

### Step 4: Create Generator Script

```python
# scripts/generate_time_samples.py
def generate_time_instant(timestamp, timezone="UTC"):
    """Generate a TimeInstant sample"""
    return {
        "@context": {...},
        "@type": "tafp5:TimeInstant",
        "@id": f"http://example.org/time/instant/{hash(timestamp)}",
        "tafp5:timestamp": {
            "@type": "xsd:dateTime",
            "@value": timestamp.isoformat()
        },
        "tafp5:timezone": timezone
    }
```

### Step 5: Generate Multiple Samples

```python
from datetime import datetime, timedelta

# Generate 10 time instant samples
base_time = datetime(2024, 11, 25, 10, 0, 0)
for i in range(10):
    time = base_time + timedelta(hours=i)
    sample = generate_time_instant(time)
    save_sample(sample, f"time_instant_{i:02d}.jsonld")
```

### Step 6: Validate All Samples

```bash
python scripts/validate_all.py --module module_90_time
```

### Step 7: Replicate for Other Modules

Once the pattern is established for Module 90:
1. Apply the same approach to Module 99
2. Then Module 03 (which depends on Module 99)
3. Continue tier by tier

---

## ✨ Key Advantages of Module-by-Module Approach

### 🎯 **Precision & Focus**
Each module is developed with full attention to its specific domain concepts, ensuring accuracy and completeness.

### 🧩 **Modularity**
Samples can be mixed and matched. A train sample from Tier 2 can reference any location from Tier 1 without tight coupling.

### 🔄 **Iterative Development**
Start simple, validate early, build confidence. Each tier builds on proven foundations.

### 📊 **Parallel Development**
Multiple team members can work on different modules simultaneously without conflicts.

### 🔍 **Focused Testing**
Each module can be thoroughly tested in isolation before integration testing.

### 📚 **Progressive Learning**
Developers learn the ontology progressively, from simple to complex concepts.

### 🛡️ **Quality Assurance**
Schema validation at each step ensures no breaking changes propagate.

### 🚀 **Scalability**
Programmatic generation allows creation of large, realistic datasets efficiently.

---

## 🔗 Reference Information

### Ontology Files
- **Main Ontology**: [`ontologies/tafp5.ttl`](../ontologies/tafp5.ttl)
- **Ontology Documentation**: [`ontologies/readme.md`](../ontologies/readme.md)

### Schema Files
- **Composite Schema**: [`Schemas/composite_schema.json`](../Schemas/composite_schema.json)
- **TAFP5 Schema**: [`Schemas/tafp5_schema.json`](../Schemas/tafp5_schema.json)
- **Consolidated Schema**: [`Schemas/cons_schema.json`](../Schemas/cons_schema.json)
- **Typography Schema**: [`Schemas/typo_schema.json`](../Schemas/typo_schema.json)

### Module Diagrams
All module diagrams are available in [`docs/images/`](../docs/images/):
- Module 01: [`TAF_revisited_01 - OperationalEntities.png`](../docs/images/TAF_revisited_01%20-%20OperationalEntities.png)
- Module 03: [`TAF_revisited_03 - OperationalLocation.png`](../docs/images/TAF_revisited_03%20-%20OperationalLocation.png)
- Module 90: [`TAF_revisited_90 - Time.png`](../docs/images/TAF_revisited_90%20-%20Time.png)
- Module 99: [`TAF_revisited_99 - Varia.png`](../docs/images/TAF_revisited_99%20-%20Varia.png)
- *(Full list available in docs/images/)*

### Documentation
- **Main Documentation**: [`docs/CDM-Telematics.pdf`](../docs/CDM-Telematics.pdf)
- **Embedded Documentation**: [`docs/CDM-Telematics_embedded.md`](../docs/CDM-Telematics_embedded.md)

### Graphol Files
- **Graphol Project**: [`Graphol/TafRevisited.graphol`](../Graphol/TafRevisited.graphol)
- **Graphol Diagrams**: [`Graphol/diagrams/`](../Graphol/diagrams/)

---

## 🚀 Getting Started

### Quick Start Guide

1. **Read the Overview** to understand the modular structure
2. **Review Module Categorization** to see dependencies
3. **Start with Tier 1** - Focus on Module 90 (Time) as your prototype
4. **Set up Python environment**:
   ```bash
   pip install rdflib pyld jsonschema faker pytest
   ```
5. **Create your first sample** manually to understand the structure
6. **Write a generator script** to automate sample creation
7. **Validate samples** against schemas
8. **Iterate and expand** to other modules

### Need Help?

- Consult the [`ontologies/readme.md`](../ontologies/readme.md) for ontology details
- Review existing samples: [`tafp5-1.ttl`](tafp5-1.ttl) and [`tafp5-1.properties`](tafp5-1.properties)
- Check schema definitions in the [`Schemas/`](../Schemas/) directory
- Reference module diagrams in [`docs/images/`](../docs/images/)

---

**Last Updated**: 2024-11-25  
**Version**: 1.0  
**Maintainer**: CDM-TAF Development Team