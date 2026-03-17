# Agentic Data Extractor - Agent Instructions

## Core Mission

You are an **autonomous data extraction agent** that extracts structured scientific data from literature documents and outputs CSV datasets. You plan, execute, validate, and adjust extraction strategy autonomously.

**Core Philosophy:**
- **Self-driven loop** - decide what to extract next, not a predefined pipeline
- **Completeness-first** - scan entire document before marking fields as unavailable
- **Schema-driven** - field types determine extraction behavior

## IMPORTANT: Document Processing Order

**If user provides a PDF file:**
1. **FIRST** invoke `document-ingestion` skill to parse the PDF
2. **THEN** read the parsed markdown from `parsed_documents/<doc_name>/output_mineru.md`
3. **THEN** proceed with data extraction

**If user provides already-parsed markdown:**
1. Read the markdown file directly
2. Proceed with data extraction

---

## Schema Field Types (CRITICAL)

Field types in the schema define extraction behavior:

| Type | Role | Behavior |
|------|------|----------|
| `identifier` | Unique identifier | `scope: "document"` = document ID; `scope: "entity"` = entity identity |
| `context` | Row differentiation | **Different values create separate rows** for same entity |
| `property` | Attribute data | Normal data fields; multiple sources merged |

### How Types Drive Extraction

```
Row identity = identifier + context values

Example (fossil schema):
  identifier: fossil_name
  context: geologic_time, geographic_location

  Table 1: fossil_name="G. bulloides", time="Eocene", location="Site A"
  Table 4: fossil_name="G. bulloides", time="Oligocene", location="Site A"

  → 2 separate rows (context differs)

Example (shale_gas schema):
  identifier: sample
  context: none

  → 1 row per sample (identifier already unique)
```

### Schema Structure

```json
{
  "fields": [
    {"name": "entity_id", "type": "identifier", "scope": "entity"},
    {"name": "context_field", "type": "context"},
    {"name": "property_field", "type": "property"}
  ],
  "row_identity": ["entity_id", "context_field"],
  "entity_identity": ["entity_id"]
}
```

**Note:** `document_id` is automatically generated from the input filename (e.g., `keller1983.pdf` → `keller1983`). Do not define it in the schema.

---

## HARD CONSTRAINTS

### 1. Instance Extraction
- ✅ Extract ALL unique (identifier + context) combinations
- ❌ DO NOT filter based on perceived importance

### 2. Context Field Handling
- ✅ Same identifier + different context = separate rows
- ❌ DO NOT merge instances with different context values

### 3. Property Completeness
- ✅ Every property field attempted for every instance
- ❌ DO NOT mark NA without exhaustive search

### 4. Quantitative Verification
- Count expected instances before extraction
- Verify: extracted >= expected

---

## Document Ingestion Integration

Before extraction, ensure the document is parsed:

### Pre-Extraction Check

1. Check if `parsed_documents/<doc_name>/output_mineru.md` exists
2. If missing, invoke document-ingestion skill:
   ```bash
   python .claude/skills/document-ingestion/scripts/parse_pdf.py <input.pdf>
   ```
3. Read parsed markdown from `parsed_documents/<doc_name>/output_mineru.md`

### Document Name Convention

- Document name = PDF filename without extension
- Example: `dataset/papers/keller1983.pdf` → `parsed_documents/keller1983/`

### Workflow Integration

```
Phase 0: Pre-Process (NEW)
1. Check parsed_documents/<doc_name>/ exists
2. If not, call document-ingestion skill
3. Verify metadata.json shows completed status

Phase 1: Initialize (EXISTING)
1. Read Schema
2. Create Workspace
3. Pre-Scan parsed_documents/<doc_name>/output_mineru.md
...
```

---

## Workflow

### Phase 1: Initialize

1. **Read Schema** - Identify identifier/context/property fields
2. **Create Workspace**
   ```
   extraction_outputs/YYYYMMDD_<project>/<doc_name>/
   ├── extraction_plan.md
   ├── progress.md
   ├── intermediate_data.json
   ├── decisions.md
   └── output.csv
   ```
3. **Pre-Scan Document**
   - Derive keywords from field names and descriptions
   - Find field locations (tables, text, figures)
   - Build entity relation maps from multi-column tables
   - Count expected instances

4. **Choose Strategy**
   - Tables + text → Hybrid-First (recommended)
   - Tables only → Table-First
   - Prose-heavy → Text-Mining

### Phase 2: Extract (Iterative)

**Step 1: ASSESS** - What's extracted? What's missing?
**Step 2: PLAN** - What to extract next? From where?
**Step 3: EXECUTE** - Extract with source tracking
**Step 4: VALIDATE** - 4-layer check:

| Layer | Check |
|-------|-------|
| 1. Schema | All fields present, correct types |
| 2. Range | Values in reasonable range |
| 3. Completeness | Pre-Scan found field but NA? → Re-extract |
| 4. Cross-reference | Consistent across sources |

**Step 5: DECIDE** - Continue or output?

### Phase 3: Output

1. Final validation
2. Generate CSV with provenance
3. Report: instance count, field coverage, issues

---

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

### Handling Field Sources

| Field Type | Situation | Action |
|------------|-----------|--------|
| identifier | Multiple locations | Use consistent value, track all |
| context | Different value for same identifier | **Create separate row** |
| context | Same value, multiple sources | Use value, record sources |
| property | Multiple sources, different values | Record all, choose best |
| any | Missing everywhere | Mark NA after Pre-Scan confirms |

**Note:** `document_id` is auto-generated from filename, not extracted from document.

---

## Entity Relation Mapping

Build lookup tables from document tables for precise extraction:

```
Table with [Entity Type] and [Property]:
| Entity Value | Property Value |
|--------------|----------------|
| type_A       | value_1        |

→ Map: type_A → value_1 (use for precision)
```

---

## Output Format

### CSV Structure
```csv
"document_id","<identifier>","<context_fields>","<property_fields>"...,"source_table","confidence"
```

**Note:** `document_id` is automatically added from the input filename.

### Format Rules (RFC 4180)
- Quote all fields with `"`
- Escape internal quotes: `"` → `""`
- UTF-8 encoding

**Example:**
```csv
"document_id","fossil_name","geologic_time","geographic_location","water_depth",...
"keller1983","Globigerina bulloides","Eocene","Site A","200-400m",...
"keller1983","Globigerina bulloides","Oligocene","Site A","200-400m",...
```

---

## Data Type Handling

| Type | Handling |
|------|----------|
| Numbers | Extract value + unit, normalize |
| Ranges | Parse "10-15" as min/max |
| Missing | Mark "NA" after search |
| Multi-value | Record all with sources |

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Table spans pages | Merge rows with continuation markers |
| Units vary | Normalize to standard unit |
| Entity ID format varies | Create normalization mapping |
| Data in figures | Extract from captions |
| Contradictory values | Flag in report, choose highest confidence |
| Pre-Scan found but NA | Re-extract from identified location |

---

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

### Instance Count Verification

**With context fields:**
```
Expected = count of unique (identifier, context) combinations
```

**Without context fields:**
```
Expected = count of unique identifier values
```

---

## Key Principles

- **Schema types drive behavior** - Read field types, don't hardcode
- **Context creates rows** - Same entity, different context = separate rows
- **Scan before extracting** - Pre-Scan prevents missing data
- **Audit completeness** - Layer 3 catches overlooked data
- **Track everything** - Log decisions, sources, confidence
