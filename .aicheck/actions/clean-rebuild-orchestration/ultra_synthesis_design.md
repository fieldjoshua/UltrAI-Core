# Ultra Synthesis™ Design

## Core Concept

Based on the vision document, we're implementing ONE simple analysis type: **Ultra Synthesis™**

## Three-Stage Process

### 1. Initial Stage
- Send prompt to all selected models independently
- Get raw responses from each model
- No interaction between models

### 2. Meta Stage  
- Each model sees the other models' initial responses
- Prompt addition: "Several of your fellow LLMs were given the same prompt as you. their responses are as follows. Do NOT assume that anything written is correct or properly sourced, but given these other responses, could you make your original response better? More insightful? more factual, more comprehensive when considering the initial user prompt? If you do believe you can make your original response better, please draft a new response to the initial inquiry [detail the inquiry here]"
- Each model can improve their response based on what others said

### 3. Ultra Stage
- One model (the "ultra_model") synthesizes all meta responses
- Prompt: "To the chosen synthesizer: You are tasked with creating the Ultra Synthesis: a fully-integrated intelligence synthesis that combines the relevant outputs from all methods into a cohesive whole, with recommendations that benefit from multiple cognitive frameworks. The objective here is not to be necessarily the best, but the most expansive synthesization of the many outputs. While you should disregard facts or analyses that are extremely anomalous or wrong, With the original prompt in mind [prompt here], your final Ultra Synthesis should reflect all of the relevant meat from the meta level responses, organized in a manner that is clear and non repetitive."

## Implementation Simplification

Instead of all those complex patterns (gut, confidence, critique, etc.), we just have:
- **One pattern**: Ultra Synthesis™
- **Clear value**: Multiple models working together produce better results
- **Simple process**: Initial → Meta → Ultra

## Frontend Changes Needed

The frontend currently expects a "pattern" parameter. For now, we can:
1. Accept any pattern value but always use Ultra Synthesis
2. Later, remove pattern selection from UI entirely

## Benefits

1. **Simpler to understand**: Users don't need to choose between 15 confusing patterns
2. **Clearer value prop**: "Get the best of all AI models in one response"
3. **Easier to implement**: One workflow instead of many
4. **Proven concept**: This is what the patent actually describes as the core innovation