# Data Extractor for OpenCode

Extract structured scientific data from parsed markdown documents into CSV datasets.

## Quick Install

Add to your `opencode.json`:

```json
{
  "plugin": ["data-extractor@file+./"]
}
```

Or install from git:

```json
{
  "plugin": ["data-extractor@git+https://github.com/foursking1/sciminer.git"]
}
```

Restart OpenCode.

## Usage

### 1. List Available Skills

```
use skill tool to list skills
```

### 2. Load Data Extractor

```
use skill tool to load data-extractor
```

### 3. Extract Data

```
Extract fossil data from parsed_documents/paper.md using the fossil schema
```

## Available Schemas

| Schema | Description |
|--------|-------------|
| `fossil` | Fossil occurrence data (species, age, location, depth) |
| `shale_gas` | Geochemical data (TOC, Ro, porosity, minerals) |

## Project Structure

```
.
├── .opencode/
│   ├── INSTALL.md                  # Installation guide
│   └── plugins/
│       └── data-extractor.js       # OpenCode plugin (auto-registers skills)
├── opencode.json                   # Plugin configuration
├── skills/
│   └── data-extractor/
│       ├── SKILL.md                # Skill definition (YAML frontmatter)
│       ├── schemas/                # Schema definitions
│       │   ├── fossil.json
│       │   └── shale_gas.json
│       └── references/             # Documentation
└── package.json                    # Entry point
```

## How It Works

The plugin (`.opencode/plugins/data-extractor.js`):

1. **Registers skills directory** via the `config` hook - adds `skills/` path to OpenCode's discovery
2. **Injects system context** via `experimental.chat.system.transform` - adds data-extractor awareness

OpenCode automatically discovers skills from registered paths that have `SKILL.md` with valid frontmatter.

## SKILL.md Format

```markdown
---
name: data-extractor
description: Use when extracting structured data from documents
allowed-tools: [Read, Write, Edit, Bash]
---

# Skill Implementation

...
```

## Updating

If installed from git:

```json
{
  "plugin": ["data-extractor@git+https://github.com/foursking1/sciminer.git#v1.0.0"]
}
```

## Troubleshooting

### Plugin not loading

```bash
opencode run --print-logs "hello" 2>&1 | grep -i data-extractor
```

### Skills not found

1. Use `skill` tool to list available skills
2. Check `SKILL.md` has valid YAML frontmatter
3. Verify plugin entry in `opencode.json`

## License

MIT
