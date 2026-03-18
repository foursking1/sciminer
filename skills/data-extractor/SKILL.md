---
name: data-extractor
description: Extract structured scientific data from PARSED markdown documents into CSV datasets. Use this skill when you have markdown files (from parsed_documents/) and need to extract tabular data using a schema. If schema doesn't exist, invoke schema-creator skill to create one. If user provides a PDF, invoke document-ingestion skill FIRST to parse it.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Data Extractor

Autonomous data extraction agent that extracts structured scientific data from literature documents and outputs CSV datasets.

**Core Philosophy:**
- **Self-driven loop** - decide what to extract next, not a predefined pipeline
- **Completeness-first** - scan entire document before marking fields as unavailable
- **Schema-driven** - field types determine extraction behavior

## When to Use This Skill

- User says "extract data from this document/paper/PDF"
- User provides a scientific paper with tables
- User has a schema file (`.json`) defining extraction fields
- User wants to convert document tables to CSV
- User mentions fossil data, geochemical data, or similar scientific datasets

## Quick Start

```
1. Check if document is parsed (parsed_documents/<doc_name>/output_mineru.md)
   - If NOT parsed: invoke document-ingestion skill FIRST
2. Resolve schema:
   - If schema_name provided: check schemas/<schema_name>.json exists
   - If schema MISSING: invoke schema-creator skill to create it
   - If no schema_name: list available schemas, or invoke schema-creator
3. Execute extraction workflow
```

## Schema Resolution (REQUIRED BEFORE EXTRACTION)

**You MUST resolve the schema BEFORE starting extraction. Do NOT skip this step.**

### Step 1: Check Schema Exists

```bash
# Check if schema file exists
ls schemas/<schema_name>.json
```

### Step 2: Handle Missing Schema

**If schema file does NOT exist, you MUST invoke schema-creator skill:**

```
Use the Skill tool to invoke schema-creator skill with:
- Document path or parsed markdown
- User's extraction requirements
- Any example output they provided
```

**Do NOT proceed with extraction until schema is resolved.**

### Step 3: Schema Selection Flow

```
User provides schema_name?
├─ YES → schemas/<schema_name>.json exists?
│         ├─ YES → Use this schema
│         └─ NO → Invoke schema-creator skill
└─ NO → List available schemas in schemas/
        ├─ User selects one → Use selected schema
        └─ User wants new → Invoke schema-creator skill
```

## Schema Field Types (CRITICAL)

| Type | Role | Behavior |
|------|------|----------|
| `identifier` | Entity identifier | `scope: "entity"` = entity identity |
| `context` | Row differentiation | **Different values create separate rows** for same entity |
| `property` | Attribute data | Normal data fields; multiple sources merged |

**Row Identity = document_id + identifier + context values**

```
Example: fossil schema
  identifier: fossil_name
  context: geologic_time, geographic_location

  fossil_name="G. bulloides", time="Eocene", location="Site A" → Row 1
  fossil_name="G. bulloides", time="Oligocene", location="Site A" → Row 2
  (Same entity, different context = 2 rows)
```

## Built-in Schemas

| Schema | Description |
|--------|-------------|
| `fossil` | Fossil occurrence data (species, age, location, depth) |
| `shale_gas` | Geochemical data (TOC, Ro, porosity, minerals) |

To use: `schemas/<schema_name>.json`

## Extraction Workflow

### Phase 1: Initialize

1. **Read Schema** - Identify identifier/context/property fields
2. **Create Workspace**
   ```
   extraction_outputs/YYYYMMDD_<project>/<doc_name>/
   ├── extraction_plan.md      # Strategy document
   ├── progress.md             # Tracking progress
   ├── intermediate_data.json  # Raw extracted data with sources
   ├── decisions.md            # Extraction decisions log
   └── output.csv              # Final output
   ```
3. **Pre-Scan Document (CRITICAL - DO NOT SKIP)**

   **You MUST scan the ENTIRE document before extraction. Incomplete scanning leads to missing data.**

   #### Step 3.1: Read Document in Chunks
   - Read the document in sections (first 500 lines, then next 500, etc.)
   - Do NOT stop after finding one data source - there may be more
   - Continue until you reach the end of the document

   #### Step 3.2: Build Data Source Inventory
   Create a comprehensive inventory:
   ```
   Data Source Inventory:
   - Table 1: [location, description, expected entities]
   - Table 2: [location, description, expected entities]
   - Text Section X: [location, entity type, expected count]
   - Figure captions: [relevant figures with data]
   - ...
   TOTAL EXPECTED INSTANCES: [sum]
   ```

   #### Step 3.3: Count Expected Instances
   - Count entities in EACH table/section separately
   - Sum all counts to get TOTAL expected instances
   - Document this count - you will verify against it later

   #### Step 3.4: Validate Scan Completeness
   Before proceeding to extraction, verify:
   - [ ] Read entire document (not just first section)
   - [ ] All tables identified and counted
   - [ ] All text-based species/entity lists found
   - [ ] Total expected instances documented

### Phase 2: Extract (Iterative Loop)

```
┌─────────────────────────────────────────┐
│  1. ASSESS: What's extracted? Missing?  │
│  2. PLAN: What to extract next?         │
│  3. EXECUTE: Extract with source track  │
│  4. VALIDATE: 4-layer check             │
│  5. DECIDE: Continue or output?         │
└─────────────────────────────────────────┘
```

**4-Layer Validation:**
| Layer | Check |
|-------|-------|
| 1. Schema | All fields present, correct types |
| 2. Range | Values in reasonable range |
| 3. Completeness | Pre-Scan found but NA? → Re-extract |
| 4. Cross-reference | Consistent across sources |

### Phase 3: Output

1. Final validation
2. Generate CSV with provenance
3. Report: instance count, field coverage, issues

## HARD CONSTRAINTS

1. **Scan ENTIRE document before extraction** - do NOT stop after finding one data source
2. **Extract ALL unique (identifier + context) combinations** - never filter based on perceived importance
3. **Same identifier + different context = separate rows** - never merge
4. **Every property attempted for every instance** - mark NA only after exhaustive search
5. **Count expected instances BEFORE extraction** - verify: extracted >= expected
6. **If extracted < expected** - STOP and re-scan document for missing data sources

## Source Tracking

For property fields, track all sources:
```json
{
  "property_field": {
    "final_value": "chosen value",
    "sources": [
      {"value": "raw value", "location": "Table 2, Row 5", "confidence": 0.95}
    ],
    "reasoning": "Why this value was chosen"
  }
}
```

## Output Format

### CSV Structure (RFC 4180)
```csv
"document_id","<identifier>","<context_fields>","<property_fields>"...,"source_table","confidence"
"keller1983","Globigerina bulloides","Eocene","Site A","200-400m",...,"Table 1",0.95
```

- Quote all fields with `"`
- Escape internal quotes: `"` → `""`
- UTF-8 encoding
- `document_id` is auto-generated from filename

## Common Issues

| Issue | Solution |
|-------|----------|
| Table spans pages | Merge rows with continuation markers |
| Units vary | Normalize to standard unit |
| Entity ID format varies | Create normalization mapping |
| Data in figures | Extract from captions |
| Contradictory values | Flag in report, choose highest confidence |

## Quality Checklist

Before marking complete:
- [ ] **ENTIRE document scanned** (not just first section)
- [ ] **Data Source Inventory completed** (all tables/sections listed)
- [ ] All instances extracted (count matches expected)
- [ ] Extracted count >= Pre-Scan expected count
- [ ] All properties attempted for all instances
- [ ] No property has >50% NA without justification
- [ ] Layer 3 Completeness Audit passed
- [ ] No duplicate instances
- [ ] Source locations recorded
- [ ] Confidence scores assigned

## Integration with Other Skills

### document-ingestion
Invoke BEFORE extraction when user provides a PDF:
```
Skill tool → document-ingestion → parse PDF → get markdown
```

### schema-creator
Invoke BEFORE extraction when schema is missing:
```
Skill tool → schema-creator → create schema → save to schemas/
```

**When to invoke schema-creator:**
- User's specified schema doesn't exist in `schemas/`
- User has no schema and wants to create one
- User asks to define extraction fields

## Reference Documentation

For detailed extraction strategies and examples, see:
- `references/extraction-strategies.md` - Strategy selection and execution details
- `schemas/` - Built-in schema files
