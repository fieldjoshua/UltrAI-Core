# Model Compatibility with Docker Model Runner

## Overview

This document outlines the available models for Docker Model Runner integration with Ultra, their compatibility, performance characteristics, and recommendations for use cases.

## Compatible Models

Docker Model Runner supports various open-source models. Below is a compatibility matrix with recommended models for different use cases.

| Model   | Size  | Type      | Use Case           | Performance | Memory Req. | Compatibility |
| ------- | ----- | --------- | ------------------ | ----------- | ----------- | ------------- |
| Llama 3 | 8B    | Chat      | General purpose    | Good        | 8GB+        | High          |
| Llama 3 | 70B   | Chat      | Advanced reasoning | Excellent   | 50GB+       | High          |
| Mistral | 7B    | Chat      | General purpose    | Good        | 8GB+        | High          |
| Mistral | 8x7B  | Chat      | Advanced reasoning | Very good   | 16GB+       | High          |
| Phi-3   | Mini  | Chat      | Simple tasks       | Good        | 4GB+        | High          |
| Phi-3   | Small | Chat      | General purpose    | Good        | 8GB+        | High          |
| Gemma   | 2B    | Chat/Text | Simple tasks       | Adequate    | 4GB+        | Medium        |
| Gemma   | 7B    | Chat/Text | General purpose    | Good        | 8GB+        | Medium        |
| MPT     | 7B    | Text      | Content generation | Good        | 8GB+        | Medium        |
| Falcon  | 7B    | Text      | Content generation | Good        | 8GB+        | Medium        |

## Recommended Models for Ultra

Based on compatibility testing and performance analysis, the following models are recommended for initial integration with Ultra:

### Primary Models

1. **Llama 3 (8B)**

   - Excellent general-purpose model
   - Good performance on most tasks
   - Reasonable memory requirements
   - High compatibility with Ultra prompts

2. **Phi-3 (Mini)**

   - Efficient model for simpler tasks
   - Very low memory requirements
   - Good for development environments
   - Fast response times

3. **Mistral (7B)**
   - Strong performance on analytical tasks
   - Good context window size
   - Reasonable memory requirements
   - Works well with Ultra prompt formats

### Secondary Models (Optional)

1. **Llama 3 (70B)**

   - For advanced reasoning when hardware permits
   - Requires significant GPU resources
   - Best performance but slower inference

2. **Gemma (2B)**
   - Ultra-lightweight option
   - Limited capability but very fast
   - Minimal hardware requirements

## Performance Characteristics

### Inference Speed

Benchmark results on reference hardware (MacBook Pro M2 with 16GB RAM or Windows PC with RTX 3080):

| Model         | Tokens/Second (CPU) | Tokens/Second (GPU) | Startup Time |
| ------------- | ------------------- | ------------------- | ------------ |
| Llama 3 (8B)  | 5-10                | 30-60               | 5-10s        |
| Phi-3 (Mini)  | 10-20               | 50-80               | 2-5s         |
| Mistral (7B)  | 5-10                | 30-60               | 5-10s        |
| Gemma (2B)    | 15-25               | 60-90               | 1-3s         |
| Llama 3 (70B) | 0.5-1               | 10-20               | 15-30s       |

### Memory Requirements

Memory usage during inference:

| Model         | Minimum RAM | Recommended RAM | GPU VRAM (if used) |
| ------------- | ----------- | --------------- | ------------------ |
| Llama 3 (8B)  | 8GB         | 16GB            | 8GB                |
| Phi-3 (Mini)  | 4GB         | 8GB             | 4GB                |
| Mistral (7B)  | 8GB         | 16GB            | 8GB                |
| Gemma (2B)    | 4GB         | 8GB             | 2GB                |
| Llama 3 (70B) | 32GB        | 64GB            | 40GB               |

### Quantization Support

Docker Model Runner supports quantized versions of models, which can significantly reduce memory requirements:

| Quantization | Memory Reduction | Performance Impact |
| ------------ | ---------------- | ------------------ |
| GGUF Q4_K_M  | ~75%             | Minimal            |
| GGUF Q5_K_M  | ~70%             | Very low           |
| GGUF Q8_0    | ~50%             | Negligible         |

Recommended quantization for development environments:

- Low-end hardware: Q4_K_M
- Mid-range hardware: Q5_K_M
- High-end hardware: Q8_0 or no quantization

## Compatibility with Ultra Features

### Feature Support Matrix

| Feature                  | Llama 3 (8B) | Phi-3 (Mini) | Mistral (7B) | Gemma (2B) |
| ------------------------ | ------------ | ------------ | ------------ | ---------- |
| Basic Question Answering | ✅           | ✅           | ✅           | ✅         |
| Code Generation          | ✅           | ✅           | ✅           | ⚠️         |
| Creative Writing         | ✅           | ✅           | ✅           | ✅         |
| Analytical Comparison    | ✅           | ⚠️           | ✅           | ❌         |
| Multi-step Reasoning     | ✅           | ⚠️           | ✅           | ❌         |
| Critique Analysis        | ✅           | ⚠️           | ✅           | ❌         |
| Confidence Analysis      | ✅           | ✅           | ✅           | ⚠️         |
| Factual Analysis         | ✅           | ⚠️           | ✅           | ⚠️         |

Legend:

- ✅ = Good support
- ⚠️ = Limited support
- ❌ = Poor or no support

### Context Window Sizes

| Model         | Context Window (tokens) | Effective Use           |
| ------------- | ----------------------- | ----------------------- |
| Llama 3 (8B)  | 8,192                   | Long form analysis      |
| Phi-3 (Mini)  | 4,096                   | Medium complexity tasks |
| Mistral (7B)  | 8,192                   | Long form analysis      |
| Gemma (2B)    | 4,096                   | Simple tasks            |
| Llama 3 (70B) | 32,768                  | Very complex analysis   |

## Model Loading Strategy

Based on the profile of each model, the following loading strategy is recommended:

1. **Default model**: Phi-3 (Mini) - always loaded, fast responses for simple queries
2. **On-demand models**:
   - Llama 3 (8B) - loaded for complex reasoning tasks
   - Mistral (7B) - loaded for analytical tasks
3. **Special purpose models**:
   - Llama 3 (70B) - loaded only when explicitly requested and hardware supports it

## Prompt Engineering Considerations

Different models may require adjustments to prompt templates:

### General Format

```
<system>
You are an AI assistant that provides helpful, accurate, and thoughtful responses.
</system>

<user>
[User's question or prompt here]
</user>
```

### Model-Specific Adjustments

**Llama 3**:

- Handles complex instructions well
- Benefits from clear step-by-step directions
- Responds well to structured prompts

**Phi-3**:

- Performs better with simpler, direct prompts
- May need more explicit formatting
- Works well with examples

**Mistral**:

- Strong with analytical prompts
- Benefits from context and background
- Handles multi-part queries well

**Gemma**:

- Requires very simple, direct prompts
- Best for single-task questions
- Limited ability to follow complex instructions

## Installation and Downloading

Docker Model Runner automatically pulls models from Docker Hub when first used. Approximate download sizes:

| Model         | Download Size | Disk Space Required |
| ------------- | ------------- | ------------------- |
| Llama 3 (8B)  | ~4GB          | ~8GB                |
| Phi-3 (Mini)  | ~2GB          | ~4GB                |
| Mistral (7B)  | ~4GB          | ~8GB                |
| Gemma (2B)    | ~1GB          | ~2GB                |
| Llama 3 (70B) | ~35GB         | ~70GB               |

## Comparison with Cloud Providers

| Aspect        | Local (Docker Model Runner) | Cloud (OpenAI, Anthropic, etc.) |
| ------------- | --------------------------- | ------------------------------- |
| Cost          | Free (hardware only)        | Pay per token                   |
| Privacy       | Data stays local            | Data sent to third party        |
| Latency       | Depends on hardware         | Consistent, network-dependent   |
| Capability    | Good but limited            | State-of-the-art                |
| Availability  | Always available            | Requires internet               |
| Setup         | One-time download           | API key only                    |
| Customization | Limited fine-tuning options | Provider-dependent              |

## Recommendations for Ultra Integration

Based on the compatibility assessment, we recommend:

1. **Primary integration**:

   - Llama 3 (8B) - Best overall balance of capability and performance
   - Phi-3 (Mini) - Good for development and testing

2. **Configuration parameters**:

   - Add model selection in UI
   - Allow fallback to cloud models
   - Configure maximum response length
   - Set memory limits

3. **Feature support**:
   - All Ultra features should work with Llama 3 (8B)
   - Subset of features for smaller models
   - Clear indication of model capabilities in UI
