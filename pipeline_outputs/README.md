# Pipeline Output Files

This directory contains saved outputs from the Ultra Synthesis™ pipeline when the `save_outputs` option is enabled.

## File Format

When `save_outputs: true` is included in an API request, the system saves two files:

### JSON Format
- **Filename**: `[user_id_]pipeline_YYYYMMDD_HHMMSS.json`
- **Content**: Complete structured data including:
  - Timestamp and metadata
  - Original input query
  - Selected models
  - Full pipeline results for each stage
  - Performance metrics and error information

### TXT Format
- **Filename**: `[user_id_]pipeline_YYYYMMDD_HHMMSS.txt`
- **Content**: Human-readable format with:
  - Header with timestamp and query
  - Each pipeline stage clearly separated
  - Formatted outputs for easy reading
  - Individual model responses, peer reviews, meta-analysis, and final synthesis

## Usage

To enable output saving, include `"save_outputs": true` in your API request:

```json
{
  "query": "Your analysis question",
  "selected_models": ["gpt-4", "claude-3-5-sonnet-20241022"],
  "save_outputs": true
}
```

The API response will include file paths in the `saved_files` field:

```json
{
  "success": true,
  "results": { ... },
  "saved_files": {
    "json_file": "pipeline_outputs/pipeline_20250617_143022.json",
    "txt_file": "pipeline_outputs/pipeline_20250617_143022.txt"
  }
}
```

## File Structure

Each saved file contains the complete pipeline execution including:
1. **Initial Response** - Parallel responses from all selected models
2. **Peer Review & Revision** - Models reviewing and revising based on peer responses
3. **Meta-Analysis** - Synthesis of peer-reviewed responses
4. **Ultra Synthesis™** - Final comprehensive response

Files are automatically timestamped and include user ID prefix when available.