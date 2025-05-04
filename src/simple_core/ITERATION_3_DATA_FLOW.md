# Modular Orchestrator Data Flow - Iteration 3

```mermaid
graph TD
    %% Client/Entry Points
    Client[Client Code] --> RequestConfig
    RequestConfig["RequestConfig\n- prompt\n- model_names\n- lead_model\n- analysis_type"] --> ModularOrc

    %% Orchestrator
    ModularOrc[modular_orchestrator.py\nModularOrchestrator] --> |"1. Process request"| CacheCheck

    %% Initial Checks
    CacheCheck{Check Cache} --> |"Cache miss"| FilterModels
    CacheCheck --> |"Cache hit"| ReturnResult

    %% Model and Analysis Selection
    FilterModels["Filter models based on\nmodel_names"] --> LeadModel
    LeadModel["Determine lead model\nfor synthesis"] --> ProcessPrompt

    %% Initial Processing
    ProcessPrompt["Format initial prompt"] --> InitialResponses
    InitialResponses["Get initial responses\nfrom selected models"] --> QualityScoring
    QualityScoring["Apply quality metrics"] --> AnalysisSelection

    %% Analysis Module Selection
    AnalysisSelection["Select analysis module\nbased on analysis_type"] --> AnalysisModule

    %% Analysis Processing
    AnalysisModule["Run selected analysis\n(comparative, factual, etc.)"] --> AnalysisManager
    AnalysisManager["analysis_manager.py\nAnalysisManager"] --> |"Execute module"| SelectedModule

    SelectedModule["Selected module\n(comparative.py, factual.py, etc.)"] --> |"analyze()"| AnalysisResults

    AnalysisResults["Standardized analysis results\n- summary\n- details\n- scores\n- recommendations"] --> Synthesis

    %% Synthesis
    Synthesis["Synthesize final response\nusing lead model"] --> ResultCreation

    %% Result Processing
    ResultCreation["Create complete result\nwith all components"] --> CacheResult
    CacheResult["Cache result"] --> ReturnResult
    ReturnResult["Return result to client"] --> Client

    %% Main Components
    subgraph "Analysis Modules"
        ComparativeAnalysis["comparative.py\nCompares responses"]
        FactualAnalysis["factual.py\nEvaluates factual accuracy"]
        OtherAnalysis["(future modules)\nreasoning.py, style.py, etc."]
    end

    AnalysisManager --> ComparativeAnalysis
    AnalysisManager --> FactualAnalysis
    AnalysisManager --> OtherAnalysis

    %% Configuration Components
    subgraph "Configuration"
        CoreConfig["config.py\nConfig & ModelDefinition"]
        AnalysisConfig["config/analysis_config.py\nAnalysisConfig"]
        ReqConfig["config/request_config.py\nRequestConfig"]
    end

    %% Support Services
    subgraph "Support Services"
        PromptTemplates["prompt_templates.py"]
        QualityMetrics["quality_metrics.py"]
        CacheService["cache_service.py"]
    end

    %% Example Data Flows
    subgraph "Example Flow: Comparative Analysis"
        ExReq["Request:\n- prompt: 'Explain quantum computing'\n- analysis_type: 'comparative'"]
        ExFilter["Filter models:\n- openai-gpt4o\n- anthropic-claude"]
        ExLead["Lead: openai-gpt4o"]
        ExInitial["Initial responses from both models"]
        ExAnalysis["Comparative analysis\nof both responses"]
        ExSynthesis["Synthesis by openai-gpt4o\nincorporating analysis"]
        ExResult["Final result with all components"]

        ExReq --> ExFilter --> ExLead --> ExInitial --> ExAnalysis --> ExSynthesis --> ExResult
    end

    subgraph "Example Flow: Factual Analysis"
        FactReq["Request:\n- prompt: 'Explain the causes of WW2'\n- analysis_type: 'factual'"]
        FactFilter["Filter models:\n- openai-gpt4o\n- anthropic-claude"]
        FactLead["Lead: anthropic-claude"]
        FactInitial["Initial responses from both models"]
        FactAnalysis["Factual analysis\nof historical accuracy"]
        FactSynthesis["Synthesis by anthropic-claude\nemphasizing factual accuracy"]
        FactResult["Final result with all components"]

        FactReq --> FactFilter --> FactLead --> FactInitial --> FactAnalysis --> FactSynthesis --> FactResult
    end

    %% Output Structure
    subgraph "Output Structure"
        Output["Complete Result"]
        OutputPrompt["prompt: string"]
        OutputInitial["initial_responses: array"]
        OutputAnalysis["analysis_results: object"]
        OutputSynthesis["synthesis: object"]
        OutputSelected["selected_response: object"]
        OutputLead["lead_model: string"]

        Output --> OutputPrompt
        Output --> OutputInitial
        Output --> OutputAnalysis
        Output --> OutputSynthesis
        Output --> OutputSelected
        Output --> OutputLead
    end
```

## Key Process Steps

1. **Request Configuration**

   - User creates a `RequestConfig` with prompt, model selection, and analysis type
   - Alternatively, user can provide a dictionary with the same information

2. **Model Selection**

   - Orchestrator filters available models based on user selection
   - If no models specified, all available models are used
   - Determines lead model for synthesis (user-specified or highest priority)

3. **Initial Response Generation**

   - Format prompt using templates
   - Send to all selected models in parallel
   - Collect and evaluate responses with quality metrics

4. **Analysis Module Selection**

   - Select appropriate analysis module based on analysis_type
   - Module is loaded and configured by the AnalysisManager

5. **Analysis Execution**

   - The selected analysis module processes the initial responses
   - Analysis is performed by the lead model if an LLM is needed
   - Standardized results are produced with summary, details, and scores

6. **Synthesis**

   - Lead model synthesizes the final response
   - Takes into account initial responses and analysis
   - Produces an optimized answer

7. **Result Creation**
   - Comprehensive result is created with all components
   - Includes initial responses, analysis, synthesis, and metadata
   - Cached for future use if the same request is made

## Data Structures

### Request Config

```python
{
  "prompt": "What are the key considerations for implementing AI in healthcare?",
  "model_names": ["openai-gpt4o", "anthropic-claude"],
  "lead_model": "anthropic-claude",
  "analysis_type": "comparative"
}
```

### Analysis Result

```python
{
  "module": "comparative",
  "summary": "Analysis summary text...",
  "details": {
    "response_count": 2,
    "prompt": "Analysis prompt text..."
  },
  "scores": {
    "openai-gpt4o": 0.85,
    "anthropic-claude": 0.92
  },
  "recommendations": [
    "Combine elements from both responses for optimal answer."
  ]
}
```

### Complete Result

```python
{
  "prompt": "Original prompt text...",
  "initial_responses": [
    {
      "model": "openai-gpt4o",
      "provider": "openai",
      "response": "Response text...",
      "response_time": 2.5,
      "quality_score": 0.85
    },
    {
      "model": "anthropic-claude",
      "provider": "anthropic",
      "response": "Response text...",
      "response_time": 3.2,
      "quality_score": 0.92
    }
  ],
  "analysis_results": {
    "modules": ["comparative"],
    "weights": {"comparative": 1.0},
    "individual_results": {
      "comparative": {
        "module": "comparative",
        "summary": "Analysis summary...",
        "details": {...},
        "scores": {...},
        "recommendations": [...]
      }
    },
    "combined_summary": "Analysis from comparative (weight: 1.00):\n..."
  },
  "synthesis": {
    "response": "Synthesized response text...",
    "model": "anthropic-claude",
    "provider": "anthropic",
    "time": 2.8
  },
  "selected_response": {
    "response": "Best individual response text...",
    "model": "anthropic-claude",
    "provider": "anthropic",
    "quality_score": 0.92
  },
  "lead_model": "anthropic-claude"
}
```
