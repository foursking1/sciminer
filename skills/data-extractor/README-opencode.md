# Data Extractor Skill for OpenCode

Extract structured scientific data from parsed markdown documents into CSV datasets.

## Installation

Add to your opencode configuration:

### Option 1: Local Installation

Add to `~/.opencode/config.json`:

```json
{
  "skills": {
    "data-extractor": {
      "path": "/home/foursking/Documents/projects/agentic-extractor/skills/data-extractor",
      "enabled": true
    }
  }
}
```

### Option 2: Git Installation

Add to `~/.opencode/config.json`:

```json
{
  "skills": {
    "data-extractor": {
      "git": "https://github.com/foursking1/sciminer.git",
      "subpath": "skills/data-extractor",
      "enabled": true
    }
  }
}
```

## Directory Structure

```
skills/data-extractor/
├── SKILL.md              # Main skill definition (required)
├── mcp-server.json       # MCP server config
├── schemas/              # Schema definitions
│   ├── fossil.json
│   └── shale_gas.json
├── references/           # Reference documentation
└── data-extractor-workspace/  # Extraction outputs
```

## Usage

Once installed, use the skill by:

1. **Extract fossil data**:
   ```
   Extract fossil data from this document using the fossil schema
   ```

2. **Extract geochemical data**:
   ```
   Extract TOC and Ro data from this shale paper
   ```

3. **With specific schema**:
   ```
   /extract --schema fossil parsed_documents/paper.md
   ```

## Available Schemas

| Schema | Description |
|--------|-------------|
| `fossil` | Fossil occurrence data (species, age, location, depth) |
| `shale_gas` | Geochemical data (TOC, Ro, porosity, minerals) |

## Requirements

- opencode >= 0.1.0
- Node.js >= 18.0.0

## License

MIT
