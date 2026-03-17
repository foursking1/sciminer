---
name: extract
description: Extract structured data from documents using a specified schema. Automatically parses PDFs if needed.
---

Extract data from the specified document(s).

## Workflow

```
1. PDF provided? → Invoke document-ingestion skill to parse → Get markdown
2. Markdown ready? → Invoke data-extractor skill with schema → Get CSV
```

## Usage

```
/extract <document_path> [schema_name] [--parallel N]
```

- `document_path`: Path to a single document OR a directory containing multiple documents
- `schema_name`: (Optional) Name of the schema to use
- `--parallel N`: (Optional) Number of parallel agents (default: 4)

## Examples

```
/extract dataset/fossil/documents/paper.pdf fossil
/extract dataset/fossil/documents/paper.pdf fossil --parallel 2
/extract dataset/fossil/documents/ fossil --parallel 8
/extract dataset/papers/
```

## What Happens

### Schema Selection

**If schema_name is provided:**
- Reads the schema from `schemas/<schema_name>.json`

**If schema_name is NOT provided:**
1. Lists available schemas in `schemas/` directory
2. Asks user to:
   - Select an existing schema, OR
   - Create a new schema (calls schema-creator skill)

### Single Document Extraction

1. Parses the document (uses document-ingestion skill if needed)
2. Extracts data following schema field types
3. Outputs CSV to `extraction_outputs/<schema_name>/<doc_name>/output.csv`

### Batch Extraction (directory)

1. Finds all documents in the directory
2. Spawns N parallel agents (default: 4)
3. Each agent extracts one document independently
4. Outputs to `extraction_outputs/<schema_name>/<doc_name>/output.csv` for each document

## Output Structure

```
extraction_outputs/
├── <schema_name>/
│   ├── <doc1_name>/
│   │   ├── output.csv
│   │   └── extraction_plan.md
│   ├── <doc2_name>/
│   │   └── output.csv
│   └── ...
```

## Notes

- Parallel agents work independently without shared state
- Each agent follows the extractor agent workflow
- Use lower parallelism for complex documents, higher for simple ones`
