# Extraction Strategies

Detailed guidance for choosing and executing extraction strategies.

## Strategy Selection

Based on document structure, choose:

| Document Type | Strategy | Approach |
|---------------|----------|----------|
| Tables + text | Hybrid-First | Tables primary, text fills gaps |
| Tables only | Table-First | Direct table extraction |
| Prose-heavy | Text-Mining | Pattern-based text extraction |

## Pre-Scan Process

Before extraction, scan the document to:

### 1. Derive Keywords

From field names and descriptions:
```
fossil_name → species, genus, foraminifera, etc.
geologic_time → age, epoch, period, Eocene, Oligocene, etc.
water_depth → depth, bathymetry, meters, etc.
```

### 2. Find Field Locations

Search for each field in:
- **Tables**: Column headers matching field names
- **Text**: Paragraphs discussing field values
- **Figures**: Captions containing data

### 3. Build Entity Relation Maps

From multi-column tables:
```
| Species | Age | Depth |
|---------|-----|-------|
| G. bulloides | Eocene | 200m |
| G. bulloides | Oligocene | 300m |

→ Map: (Species, Age) → Depth
```

### 4. Count Expected Instances

```
With context fields: Expected = count of unique (identifier, context)
Without context: Expected = count of unique identifier values
```

## Extraction Execution

### Table Extraction

1. **Locate all tables** with relevant data
2. **Parse table structure**: headers, rows, spanning cells
3. **Map columns to fields**: direct or inferred
4. **Extract rows**: handle multi-page tables, merged cells
5. **Validate**: check for missing/invalid values

### Text Extraction

1. **Identify relevant sections** using keywords
2. **Extract values** with surrounding context
3. **Associate with entity**: use proximity, explicit references
4. **Handle variations**: synonyms, abbreviations

### Figure Extraction

1. **Read captions** for data values
2. **Extract from charts** if possible (via description)
3. **Cross-reference** with text

## Source Tracking Format

### Identifier Sources
```
"fossil_name": {
  "final_value": "Globigerina bulloides",
  "sources": [
    {"value": "G. bulloides", "location": "Table 1, Row 1", "confidence": 1.0},
    {"value": "Globigerina bulloides", "location": "Text, p. 5", "confidence": 1.0}
  ],
  "reasoning": "Consistent across all sources"
}
```

### Context Sources (Different Values → Separate Rows)
```
"geologic_time": {
  "value": "Eocene",
  "sources": [{"value": "Eocene", "location": "Table 1", "confidence": 1.0}],
  "row_key": true  // Different values create separate rows
}
```

### Property Sources (Multiple Values → Choose Best)
```
"water_depth": {
  "final_value": "200-400m",
  "sources": [
    {"value": "200-400m", "location": "Table 2, Row 5", "confidence": 0.95},
    {"value": "~300m", "location": "Text, p. 8", "confidence": 0.7}
  ],
  "reasoning": "Table value more precise, text confirms range"
}
```

## Validation Details

### Layer 1: Schema Validation
- All required fields present
- Field types correct
- Data types match schema

### Layer 2: Range Validation
- Numeric values within reasonable bounds
- Dates within expected periods
- Strings match expected patterns

### Layer 3: Completeness Audit
- Compare extracted vs. Pre-Scan findings
- If Pre-Scan found field but extraction returned NA:
  - Re-extract from identified location
  - Document why extraction failed

### Layer 4: Cross-Reference Validation
- Check consistency across sources
- Flag contradictions
- Choose highest confidence value

## Handling Edge Cases

### Multi-Page Tables

```
Table 1 (continued from previous page)
| Species | Age |
|---------|-----|
| ... continued ... |

→ Merge with previous page's table portion
```

### Merged Cells

```
| Species   | Age     |
|-----------|---------|
| G. bull.  | Eocene  |
|           | Oligocene |  ← Same species, different age

→ Create separate rows for each
```

### Unit Variations

```
Table 1: depth = "200-400m"
Table 2: depth = "0.2-0.4 km"

→ Normalize to standard unit (meters)
```

### Entity Name Variations

```
Table 1: "Globigerina bulloides"
Table 2: "G. bulloides"
Text: "Globigerina bull."

→ Create normalization map, use full name
```

## Instance Counting

### With Context Fields
```
fossil_name + geologic_time + geographic_location = row identity

Count unique combinations:
- G. bulloides + Eocene + Site A = 1
- G. bulloides + Oligocene + Site A = 1
- G. bulloides + Eocene + Site B = 1

Expected = 3 instances
```

### Without Context Fields
```
sample_id = row identity

Count unique values:
- Sample-1 = 1
- Sample-2 = 1

Expected = 2 instances
```

## Output Report

After extraction, generate report:

```markdown
# Extraction Report: <doc_name>

## Summary
- Document: keller1983.pdf
- Schema: fossil
- Total instances: 15

## Field Coverage
| Field | Coverage | Notes |
|-------|----------|-------|
| fossil_name | 100% (15/15) | - |
| geologic_time | 100% (15/15) | - |
| water_depth | 87% (13/15) | 2 NA (not in document) |
| latitude | 0% (0/15) | Not found in document |

## Issues
- Table 3 spans pages 4-5: merged successfully
- Unit variation in depth: normalized to meters
- Figure 2 contains additional data: extracted from caption

## Sources Used
- Table 1: Species names and ages
- Table 2: Water depths
- Text p. 8: Additional depth values
- Figure 2 caption: Location coordinates
```
