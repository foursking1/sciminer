---
name: document-ingestion
description: Parse PDF documents to Markdown using MinerU. Use this skill whenever you need to convert PDFs to markdown, extract text from scientific papers, or prepare documents for the extraction agent. Automatically caches parsed results to avoid re-processing.
allowed-tools: [Read, Bash]
---

# Document Ingestion

Parse PDF documents to Markdown format for the extraction agent. Results are cached in `parsed_documents/` for reuse.

## Quick Start

```bash
python .claude/skills/document-ingestion/scripts/parse_pdf.py <input.pdf>
```

Output will be saved to `parsed_documents/<doc_name>/`.

## Directory Structure

```
project_root/
├── dataset/papers/              # Source PDFs (input)
│   └── paper1.pdf
│
├── parsed_documents/            # Parsed results (cache)
│   └── paper1/
│       ├── output_mineru.md     # Markdown content
│       ├── images/              # Extracted figures
│       └── metadata.json        # Parse status, method, timestamp
│
└── extraction_outputs/          # Agent extraction results
    └── <project>/<doc_name>/
```

## Usage

### Basic Usage

```bash
# Parse a PDF (uses default output directory)
python .claude/skills/document-ingestion/scripts/parse_pdf.py paper.pdf

# Force re-parse (ignore cache)
python .claude/skills/document-ingestion/scripts/parse_pdf.py paper.pdf --force
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input.pdf` | Path to the PDF file |
| `-o, --output <dir>` | Output directory (default: `parsed_documents/<doc_name>/`) |
| `-m, --method <type>` | Parse method: `txt`, `ocr`, or `auto` (default: auto) |
| `-f, --force` | Force re-parse even if cached version exists |

### Parse Methods

| Method | Use Case |
|--------|----------|
| `txt` | Text-based PDFs (most scientific papers) |
| `ocr` | Scanned PDFs / images |
| `auto` | Auto-detect PDF type |

## Caching Behavior

The script automatically checks if a document is already parsed:

1. **Cache hit:** If `parsed_documents/<doc_name>/metadata.json` exists and source file unchanged, returns cached result
2. **Cache miss:** Parses the document and saves to cache
3. **Force:** Use `--force` to re-parse regardless of cache

## Output Files

After parsing, the output directory contains:

```
parsed_documents/<doc_name>/
├── output_mineru.md     # Main markdown content
├── images/              # Extracted figures (if any)
└── metadata.json        # Parse metadata
```

### metadata.json Structure

```json
{
  "source_file": "paper.pdf",
  "source_hash": "abc12345",
  "parse_method": "txt",
  "parse_time": "2026-03-16T11:30:00",
  "output_char_count": 71307,
  "output_dir": "parsed_documents/paper",
  "status": "completed"
}
```

## Integration with Extractor Agent

The extractor agent should:

1. Check if `parsed_documents/<doc_name>/output_mineru.md` exists
2. If not, call this skill to parse
3. Read the markdown for extraction

## Features

- **Layout Analysis**: Detects titles, paragraphs, tables, figures
- **Table Recognition**: Converts tables to Markdown format
- **Image Extraction**: Saves figures to `images/` directory
- **Formula Support**: Outputs LaTeX for equations
- **Smart Caching**: Avoids re-parsing unchanged documents

## Requirements

- PaddleOCR 2.8.1
- PaddlePaddle 2.6.2
- Config file: `~/magic-pdf.json`

If not installed:
```bash
pip install paddleocr==2.8.1 paddlepaddle==2.6.2
```
