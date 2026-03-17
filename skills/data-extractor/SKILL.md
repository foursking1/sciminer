---
name: data-extractor
description: Extract structured scientific data from PARSED markdown documents into CSV datasets. Use this skill when you have markdown files (from parsed_documents/) and need to extract tabular data using a schema. This skill expects already-parsed markdown input. If user provides a PDF, invoke document-ingestion skill FIRST to parse it.
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
2. If not, use document-ingestion skill to parse
3. Read the extraction schema
4. Execute extraction workflow
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
3. **Pre-Scan Document**
   - Derive keywords from field names
   - Find field locations (tables, text, figures)
   - Build entity relation maps
   - Count expected instances

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

1. **Extract ALL unique (identifier + context) combinations** - never filter
2. **Same identifier + different context = separate rows** - never merge
3. **Every property attempted for every instance** - mark NA only after exhaustive search
4. **Count expected instances before extraction** - verify: extracted >= expected

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
- [ ] All instances extracted (count matches expected)
- [ ] All properties attempted for all instances
- [ ] No property has >50% NA without justification
- [ ] Pre-Scan completed
- [ ] Layer 3 Completeness Audit passed
- [ ] No duplicate instances
- [ ] Source locations recorded
- [ ] Confidence scores assigned

## Integration with Other Skills

- **document-ingestion**: Use to parse PDFs before extraction
- **schema-creator**: Use to create new extraction schemas

## Reference Documentation

For detailed extraction strategies and examples, see:
- `references/extraction-strategies.md` - Strategy selection and execution details
- `schemas/` - Built-in schema files
