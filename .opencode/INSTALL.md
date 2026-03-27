# Data Extractor for OpenCode

## Installation

Add to your `opencode.json` (project-level) or `~/.config/opencode/opencode.json` (global):

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

Restart OpenCode. The plugin auto-registers all skills.

## Usage

### List Available Skills

```
use skill tool to list skills
```

### Use Data Extractor

```
use skill tool to load data-extractor
```

Then ask it to extract data from your documents.

## Available Schemas

| Schema | Description |
|--------|-------------|
| `fossil` | Fossil occurrence data |
| `shale_gas` | Geochemical data (TOC, Ro, porosity) |

## Directory Structure

```
skills/data-extractor/
├── SKILL.md              # Skill definition
├── schemas/
│   ├── fossil.json
│   └── shale_gas.json
└── references/
```

## How It Works

The plugin (`.opencode/plugins/data-extractor.js`):

1. **Registers skills directory** via the `config` hook
2. **Injects bootstrap context** via `experimental.chat.system.transform`

OpenCode discovers skills from the registered paths automatically.

## Troubleshooting

### Skills not appearing

1. Check plugin is loading: `opencode run --print-logs "hello" 2>&1 | grep -i data-extractor`
2. Verify `opencode.json` plugin entry
3. Each skill needs `SKILL.md` with valid YAML frontmatter
