# Installing Data Extractor Skill for OpenCode

## Quick Start

### Step 1: Clone or Copy the Skill

```bash
# Option A: Clone the repository
git clone https://github.com/foursking1/sciminer.git
cd sciminer

# Option B: Copy just the skill directory
cp -r skills/data-extractor ~/my-opencode-skills/
```

### Step 2: Configure OpenCode

Add to your opencode config file (`~/.config/opencode/config.json` or `~/.opencode/config.json`):

```json
{
  "skills": {
    "data-extractor": {
      "path": "/path/to/skills/data-extractor",
      "enabled": true
    }
  }
}
```

Or use a relative path if opencode is started from the project root:

```json
{
  "skills": {
    "data-extractor": {
      "path": "./skills/data-extractor",
      "enabled": true
    }
  }
}
```

### Step 3: Verify Installation

In opencode, run:

```
/skills
```

You should see `data-extractor` in the list.

## Directory Structure Required by OpenCode

```
skills/data-extractor/
├── SKILL.md              # REQUIRED: Skill definition with frontmatter
├── schemas/              # OPTIONAL: Schema definitions
│   ├── fossil.json
│   └── shale_gas.json
├── references/           # OPTIONAL: Documentation
└── README.md             # OPTIONAL: User documentation
```

## SKILL.md Frontmatter Format

```markdown
---
name: data-extractor
description: Extract structured scientific data from parsed markdown documents
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Skill implementation...
```

### Required Frontmatter Fields

| Field | Description |
|-------|-------------|
| `name` | Unique skill identifier (used for triggering) |
| `description` | When this skill should be used |
| `allowed-tools` | Tools the skill can access |

## Usage Examples

Once installed:

```
# Extract fossil data
Extract all fossil species from this document

# Extract with specific schema
Use the fossil schema to extract data from parsed_documents/paper.md

# Extract geochemical data
Extract TOC, Ro, and porosity data from this shale gas paper
```

## Troubleshooting

### Skill not appearing in /skills list

1. Check the SKILL.md frontmatter is valid YAML
2. Verify the path in config.json is correct
3. Restart opencode

### Skill not triggering automatically

1. Check the `description` field - it should match user queries
2. Try explicit invocation: `Use the data-extractor skill to...`

## See Also

- [OpenCode Skills Documentation](https://opencode.ai/docs/skills/)
- [SKILL.md Format Reference](https://opencode.ai/docs/skill-format/)
