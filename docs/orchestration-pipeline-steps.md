# UltrAI Orchestration Pipeline: Step-by-Step Process

## Overview
This document outlines the expected prompts and outputs at each stage of the UltrAI 3-stage orchestration pipeline.

## Universal Template Variables

Replace these variables with actual user input:
- `[USER_INPUT]` - The actual user query (e.g., "What is 2+2?", "Explain machine learning", etc.)
- `[QUERY_TYPE]` - Detected query type (general, technical, creative, analytical, procedural)
- `[MODEL_1]`, `[MODEL_2]`, `[MODEL_3]` - Selected AI models (e.g., gpt-4o, claude-3-5-sonnet, gemini-1.5-pro)
- `[INITIAL_RESPONSE_1]`, `[INITIAL_RESPONSE_2]`, `[INITIAL_RESPONSE_3]` - Each model's initial response
- `[PROVIDER_1]`, `[PROVIDER_2]`, `[PROVIDER_3]` - Model providers (openai, anthropic, google)

## Pipeline Stages

### Stage 1: Initial Response Generation

| Step | Input/Prompt | Expected Output |
|------|--------------|-----------------|
| **1.1 User Query** | User: `[USER_INPUT]`<br><br>Examples:<br>• "What is 2+2?"<br>• "Explain quantum entanglement"<br>• "Write a Python function to sort a list"<br>• "What are the causes of climate change?"<br>• "How do I start a small business?" | Query received and validated<br>Type: `[QUERY_TYPE]`<br>• general<br>• technical<br>• creative<br>• analytical<br>• procedural |
| **1.2 Model Selection** | System selects 3+ models based on:<br>• Query complexity<br>• Available models<br>• Provider diversity requirement<br>• Model performance history | Selected models:<br>• `[MODEL_1]` (Provider 1)<br>• `[MODEL_2]` (Provider 2)<br>• `[MODEL_3]` (Provider 3)<br><br>Example combinations:<br>• `gpt-4o`, `claude-3-5-sonnet`, `gemini-1.5-pro`<br>• `gpt-4`, `claude-3-haiku`, `gemini-1.5-flash`<br>• `gpt-4-turbo`, `claude-3-5-sonnet`, `gemini-pro` |
| **1.3 Concurrent Execution** | Each model receives the exact user query:<br>`[USER_INPUT]`<br><br>No meta-prompting or modification | Parallel API calls initiated:<br>• API Call 1 → Model 1<br>• API Call 2 → Model 2  <br>• API Call 3 → Model 3<br><br>Timeout: 60 seconds per model |
| **1.4 Model Responses** | Direct query to each model without system prompts | Model 1: `[INITIAL_RESPONSE_1]`<br>Model 2: `[INITIAL_RESPONSE_2]`<br>Model 3: `[INITIAL_RESPONSE_3]`<br><br>Response characteristics:<br>• Length: Variable (50-2000 tokens)<br>• Style: Model-specific<br>• Content: Direct answer to query |
| **1.5 Response Collection** | System collects all successful responses | ```json<br>{<br>  "stage": "initial_response",<br>  "responses": {<br>    "[MODEL_1]": "[INITIAL_RESPONSE_1]",<br>    "[MODEL_2]": "[INITIAL_RESPONSE_2]",<br>    "[MODEL_3]": "[INITIAL_RESPONSE_3]"<br>  },<br>  "prompt": "[USER_INPUT]",<br>  "successful_models": ["[MODEL_1]", "[MODEL_2]", "[MODEL_3]"],<br>  "response_count": 3<br>}<br>``` |

### Stage 2: Peer Review and Revision

| Step | Input/Prompt | Expected Output |
|------|--------------|-----------------|
| **2.1 Peer Review Setup** | Each model reviews others' responses | Review assignments created |
| **2.2 GPT-4o Review** | "Original query: What is 2+2?<br><br>Other models responded:<br>**Claude:** 2+2 = 4...<br>**Gemini:** The sum of 2 and 2 is 4...<br><br>Based on these peer insights, provide your revised response." | "After reviewing peer responses, I confirm that 2+2 = 4. All models correctly identified this fundamental arithmetic fact..." |
| **2.3 Claude Review** | Similar prompt with GPT-4o and Gemini responses | "Having considered the other models' responses, 2+2 indeed equals 4. The consensus reinforces..." |
| **2.4 Gemini Review** | Similar prompt with GPT-4o and Claude responses | "All models agree that 2+2 = 4. This mathematical fact is universally consistent..." |
| **2.5 Revision Collection** | System collects all revised responses | `revised_responses: {model1: "revised...", model2: "revised...", model3: "revised..."}` |

### Stage 3: Ultra Synthesis

| Step | Input/Prompt | Expected Output |
|------|--------------|-----------------|
| **3.1 Synthesis Model Selection** | System selects best-performing model | Selected: `claude-3-5-sonnet` (based on quality scores) |
| **3.2 Synthesis Prompt** | "Given the user's initial query, please review the revised drafts from all LLMs. Keep commentary to a minimum unless it helps with the original inquiry. Do not reference the process, but produce the best, most thorough answer to the original query.<br><br>ORIGINAL QUERY: What is 2+2?<br><br>REVISED LLM DRAFTS:<br>**gpt-4o (Peer-Reviewed):** After reviewing peer responses...<br>**claude-3-5-sonnet (Peer-Reviewed):** Having considered...<br>**gemini-1.5-pro (Peer-Reviewed):** All models agree...<br><br>Create a comprehensive Ultra Synthesis™ document that directly answers the original query with maximum thoroughness." | "**Answer: 4**<br><br>The sum of 2 and 2 equals 4. This is a fundamental principle of arithmetic that remains constant across all number systems using standard addition.<br><br>**Key Points:**<br>• Basic addition: 2 + 2 = 4<br>• This represents combining two groups of two units<br>• The result is universally consistent in base-10 mathematics<br>• This operation demonstrates the commutative property of addition<br><br>**Mathematical Context:**<br>This calculation is one of the first arithmetic operations taught in mathematics education, serving as a foundation for understanding number relationships and more complex mathematical concepts." |

## Error Scenarios

### Insufficient Models Scenario

| Condition | System Response |
|-----------|----------------|
| Only 1 model available | HTTP 503: "UltrAI requires at least 3 models and providers: ['anthropic', 'google', 'openai']" |
| Only 2 models available | HTTP 503: "Service requires minimum 3 models for full pipeline" |
| Missing required provider | HTTP 503: "Missing required providers: ['anthropic']" |

### Degraded Mode (if enabled)

| Condition | Pipeline Adjustment |
|-----------|---------------------|
| 2 models available | - Skip peer review stage<br>- Direct to synthesis using initial responses<br>- Warning: "Operating in degraded mode" |
| 1 model available | - Single model response only<br>- No peer review or synthesis<br>- Warning: "Single model fallback" |

## SSE Event Flow

| Event | When Triggered | Data |
|-------|---------------|------|
| `analysis_start` | Pipeline begins | `{models: ["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"]}` |
| `model_selected` | Each model selected | `{model: "gpt-4o"}` |
| `initial_start` | Stage 1 begins | `{}` |
| `model_completed` | Each model completes | `{model: "gpt-4o"}` |
| `pipeline_complete` | All stages done | `{}` |
| `analysis_complete` | Final completion | `{processing_time: 12.5, stages: ["initial_response", "peer_review", "ultra_synthesis"]}` |

## Configuration Requirements

```yaml
# Minimum viable configuration
MINIMUM_MODELS_REQUIRED: 3
REQUIRED_PROVIDERS: ["openai", "anthropic", "google"]
ENABLE_SINGLE_MODEL_FALLBACK: false

# API Keys Required
OPENAI_API_KEY: required
ANTHROPIC_API_KEY: required  
GOOGLE_API_KEY: required
```

## Quality Indicators in Synthesis

The Ultra Synthesis includes quality metrics:
- **Overall Confidence**: High/Moderate/Low based on consensus
- **Consensus Level**: Excellent/Good/Mixed based on agreement
- **Contributing Models**: Number of perspectives integrated

## Example Complex Query

### Query: "Explain quantum entanglement"

| Stage | Key Output Elements |
|-------|-------------------|
| Initial Responses | Each model provides technical explanation |
| Peer Review | Models refine based on others' approaches |
| Ultra Synthesis | - Unified explanation combining best elements<br>- Technical accuracy from all sources<br>- Analogies and examples from multiple perspectives<br>- Comprehensive coverage without redundancy |