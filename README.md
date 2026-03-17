# sciminer

Claude Code skills for autonomous data extraction from scientific documents. Extract structured data from PDFs using AI-powered agents.

## Features

- **Autonomous Extraction**: AI agent plans, executes, and validates extraction strategy
- **Schema-Driven**: Define what to extract with JSON schemas
- **Batch Processing**: Parallel extraction from multiple documents
- **Smart Caching**: Parsed documents are cached for reuse
- **PDF Support**: Parse scientific papers with MinerU (tables, figures, equations)

## Installation

```bash
npm install sciminer
```

## Quick Start

### 1. Create a Schema

Define what data to extract:

```bash
# Use schema-creator skill
/schema-creator

# Or copy an example schema
cp examples/schemas/fossil.json schemas/fossil.json
```

### 2. Extract Data

Single document:

```
/extract dataset/papers/paper.pdf fossil
```

Multiple documents in parallel:

```
/extract dataset/papers/ fossil --parallel 8
```

## Commands

| Command | Description |
|---------|-------------|
| `/extract <path> [schema]` | Extract data from document(s) |
| `/extract <path> [schema] --parallel N` | Batch extraction with N parallel agents |

## Skills

| Skill | Description |
|-------|-------------|
| `document-ingestion` | Parse PDFs to Markdown using MinerU |
| `schema-creator` | Create extraction schemas interactively |

## Schema Structure

```json
{
  "schema_name": "example",
  "fields": [
    {"name": "entity_id", "type": "identifier", "scope": "entity"},
    {"name": "time_period", "type": "context"},
    {"name": "property_1", "type": "property"}
  ],
  "row_identity": ["entity_id", "time_period"],
  "entity_identity": ["entity_id"]
}
```

### Field Types

| Type | Purpose |
|------|---------|
| `identifier` | Entity identifier (species, sample, etc.) |
| `context` | Creates separate rows for different values |
| `property` | Data fields to extract |

## Directory Structure

```
project/
├── dataset/papers/           # Source PDFs
├── schemas/                  # Extraction schemas
├── parsed_documents/         # Cached parsed PDFs
└── extraction_outputs/       # Extraction results
```

## Output

Extraction produces:

```
extraction_outputs/
└── <schema_name>/
    └── <doc_name>/
        ├── output.csv         # Extracted data
        ├── extraction_plan.md # Strategy used
        └── decisions.md       # Extraction decisions
```

## Examples

See [examples/workflow.md](examples/workflow.md) for a complete workflow example.

Example schemas:
- [fossil.json](examples/schemas/fossil.json) - Paleontology data extraction
- [shale_gas.json](examples/schemas/shale_gas.json) - Geochemical data extraction

## Requirements

For PDF parsing:
- PaddleOCR 2.8.1
- PaddlePaddle 2.6.2

```bash
pip install paddleocr==2.8.1 paddlepaddle==2.6.2
```

## License

MIT
