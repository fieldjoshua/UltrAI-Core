# Local Models Compatibility

This document provides information about the compatibility of various open-source models with Docker Model Runner and Ultra.

## Overview

Docker Model Runner supports a variety of open-source language models that can be used with Ultra. These models differ in size, performance, capabilities, and resource requirements.

## Supported Model Architectures

Docker Model Runner currently supports the following model architectures:

- Llama (llama.cpp backend)
- Phi
- Mistral
- Gemma
- Falcon

## Model Listing and Selection

To see all available models:

```bash
docker model list
```

To pull a specific model:

```bash
docker model pull <model_name>
```

## Model Compatibility Matrix

The following table provides compatibility information for common models used with Ultra:

| Model Name | Size   | Memory Required | GPU Support | Strengths                                  | Limitations                          |
| ---------- | ------ | --------------- | ----------- | ------------------------------------------ | ------------------------------------ |
| ai/smollm2 | ~250MB | 1GB             | Yes         | Fast, minimal resources, good for testing  | Limited reasoning, shorter responses |
| ai/mistral | ~4GB   | 8GB             | Yes         | Good reasoning, balanced performance       | Moderate resource requirements       |
| ai/llama3  | ~8GB   | 16GB            | Yes         | Strong reasoning, detailed responses       | Higher resource requirements         |
| ai/phi3    | ~1.5GB | 4GB             | Yes         | Efficient, good instruction following      | May struggle with complex tasks      |
| ai/gemma   | ~3GB   | 8GB             | Yes         | Google's efficient model, strong reasoning | Limited coding capabilities          |
| ai/falcon  | ~5GB   | 12GB            | Yes         | Strong factual knowledge                   | Higher resource requirements         |

## Performance Characteristics

### Response Speed

Response speed is affected by several factors:

1. **Model Size**: Smaller models generally respond faster
2. **Hardware**: GPU acceleration significantly improves performance
3. **Prompt Length**: Longer prompts take more time to process
4. **Response Length**: Generating longer responses takes more time

Approximate response times for "What is machine learning?" (GPU accelerated):

| Model      | Response Time |
| ---------- | ------------- |
| ai/smollm2 | 1-2 seconds   |
| ai/mistral | 3-5 seconds   |
| ai/llama3  | 5-10 seconds  |

### Memory Usage

Memory requirements scale with model size:

| Model Size     | Minimum RAM | Recommended RAM |
| -------------- | ----------- | --------------- |
| Small (<2GB)   | 4GB         | 8GB             |
| Medium (2-5GB) | 8GB         | 16GB            |
| Large (>5GB)   | 16GB        | 32GB+           |

### GPU Acceleration

GPU acceleration is automatically used when available and provides:

- 3-10x faster inference speed
- Better handling of concurrent requests
- Ability to run larger models efficiently

## Feature Support Matrix

Different models have varying capabilities in these areas:

| Feature               | ai/smollm2 | ai/mistral | ai/llama3 | ai/phi3 |
| --------------------- | ---------- | ---------- | --------- | ------- |
| Text Generation       | ✅         | ✅         | ✅        | ✅      |
| Context Length        | 4K         | 8K         | 8K        | 4K      |
| Reasoning             | ⚠️         | ✅         | ✅        | ✅      |
| Code Generation       | ⚠️         | ✅         | ✅        | ⚠️      |
| Instruction Following | ✅         | ✅         | ✅        | ✅      |
| Multilingual          | ⚠️         | ✅         | ✅        | ⚠️      |
| Factual Knowledge     | ⚠️         | ✅         | ✅        | ✅      |

Legend:

- ✅ Strong capability
- ⚠️ Limited capability
- ❌ Not supported

## Model Selection Guidelines

### For Development

For development work, use:

- ai/smollm2: Fastest, minimal resources
- ai/phi3: Good balance of quality and performance

### For Testing

For comprehensive testing, use:

- ai/mistral: Good general-purpose performance
- ai/llama3: High-quality responses

### For Production

For production-like environments, use:

- ai/llama3: Best overall quality
- ai/mistral: Good quality with lower resource requirements

## Resource Requirements

### CPU

Docker Model Runner uses CPU for inference when GPU is not available:

- Small models: 2+ CPU cores
- Medium models: 4+ CPU cores
- Large models: 8+ CPU cores

### Memory

Memory requirements by model size:

- Small models (<2GB): 4GB+ RAM
- Medium models (2-5GB): 8GB+ RAM
- Large models (>5GB): 16GB+ RAM

### Storage

Storage requirements include:

- Docker Desktop installation: ~2GB
- Each model: Size varies from 250MB to 10GB+
- Model cache: Additional 50-100% of model size

## Known Limitations

### General Limitations

1. **Offline Knowledge**: Models only have knowledge from their training data
2. **Performance Variability**: Response quality and speed may vary between runs
3. **Resource Intensity**: Larger models require significant system resources

### Model-Specific Limitations

1. **ai/smollm2**:

   - Limited context understanding
   - May generate incorrect information more frequently
   - Shorter responses

2. **ai/mistral**:

   - Sometimes repetitive in longer generations
   - May have inconsistent coding abilities

3. **ai/llama3**:
   - Higher resource requirements
   - Slower response times on CPU-only systems

## Optimization Strategies

### System Optimization

1. **GPU Acceleration**: Use systems with compatible GPUs
2. **Memory Allocation**: Allocate additional memory to Docker Desktop
3. **Resource Monitoring**: Monitor resource usage during model runs

### Model Optimization

1. **Quantization**: Use quantized models for faster inference
2. **Prompt Engineering**: Keep prompts concise and clear
3. **Context Management**: Limit context size for better performance

## Future Compatibility

Docker Model Runner is continuously updated with support for new models. Check for updates by:

1. Keeping Docker Desktop updated
2. Running `docker model list` to see newly available models
3. Checking Docker Model Runner documentation for announcements
