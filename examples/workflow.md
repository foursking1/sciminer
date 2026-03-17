# Agentic Extractor - Workflow Example

This guide demonstrates a complete workflow for extracting data from scientific papers.

## Quick Start

### 1. Install the Package

```bash
npm install agentic-extractor
```

The skills, agents, and commands will be available in your Claude Code project.

### 2. Create a Schema

Use the schema-creator skill to define what data to extract:

```
/schema-creator

# Then describe what you need:
"I want to extract fossil occurrence data from paleontology papers"
```

Or use an existing schema from `examples/schemas/`:

```bash
cp examples/schemas/fossil.json schemas/fossil.json
```

### 3. Prepare Your Documents

Place your PDF documents in a directory:

```
project/
├── dataset/
│   └── papers/
│       ├── paper1.pdf
│       └── paper2.pdf
```

### 4. Run Extraction

Single document:

```
/extract dataset/papers/paper1.pdf fossil
```

Batch extraction with parallel processing:

```
/extract dataset/papers/ fossil --parallel 8
```

## Complete Example: Fossil Data Extraction

### Step 1: Schema Setup

Create `schemas/fossil.json`:

```json
{
  "schema_name": "fossil",
  "fields": [
    {"name": "fossil_name", "type": "identifier", "scope": "entity"},
    {"name": "geologic_time", "type": "context"},
    {"name": "geographic_location", "type": "context"},
    {"name": "water_depth", "type": "property"}
  ],
  "row_identity": ["fossil_name", "geologic_time", "geographic_location"],
  "entity_identity": ["fossil_name"]
}
```

### Step 2: Document Parsing

The extractor automatically parses PDFs using the document-ingestion skill. Parsed documents are cached:

```
parsed_documents/
├── paper1/
│   ├── output_mineru.md    # Markdown content
│   ├── images/             # Extracted figures
│   └── metadata.json       # Parse status
```

### Step 3: Extraction

```
/extract dataset/papers/paper1.pdf fossil
```

### Step 4: Review Output

```
extraction_outputs/
└── fossil/
    └── paper1/
        ├── output.csv           # Extracted data
        ├── extraction_plan.md   # Strategy used
        └── decisions.md         # Extraction decisions
```

**output.csv:**

```csv
"document_id","fossil_name","geologic_time","geographic_location","water_depth"
"paper1","Globigerina bulloides","Eocene","Site A","200-400m"
"paper1","Globigerina bulloides","Oligocene","Site A","200-400m"
```

## Schema Field Types

| Type | Behavior |
|------|----------|
| `identifier` | Uniquely identifies each entity (e.g., species name) |
| `context` | Different values create separate rows |
| `property` | Normal data fields |

### Context Field Example

Same fossil found in different time periods creates multiple rows:

| fossil_name | geologic_time | water_depth |
|-------------|---------------|-------------|
| G. bulloides | Eocene | 200-400m |
| G. bulloides | Oligocene | 200-400m |

## Parallel Processing

For batch extraction, use `--parallel N`:

```
/extract dataset/papers/ fossil --parallel 8
```

- Each document processed by an independent agent
- Default parallelism: 4
- Use higher values for simple documents, lower for complex ones

## Tips

1. **Check the pre-scan**: Review `extraction_plan.md` to see what the agent found
2. **Verify completeness**: Compare extracted rows with expected instances
3. **Review decisions**: Check `decisions.md` for ambiguous cases
4. **Iterate on schema**: Refine field descriptions if extraction misses data
