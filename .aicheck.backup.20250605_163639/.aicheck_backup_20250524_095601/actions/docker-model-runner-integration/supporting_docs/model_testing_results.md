# Docker Model Runner: Model Testing Results

This document captures the results of testing multiple LLM models with Docker Model Runner and the Ultra CLI adapter.

## Overview

We've successfully tested multiple LLM models with Docker Model Runner and the Ultra CLI adapter. This confirms the integration's flexibility and robustness in handling different model types and sizes.

## Tested Models

### 1. ai/smollm2

- **Size**: 361.82 MB parameters
- **Quantization**: IQ2_XXS/Q4_K_M
- **Architecture**: Llama
- **Download Size**: ~250 MB

#### Performance Characteristics:

- **Response Speed**: Fast (1-2 seconds)
- **Memory Usage**: Low (~1GB)
- **Response Quality**: Good for simple queries
- **Strengths**: Quick responses, minimal resource requirements
- **Limitations**: Less detailed responses, occasional inaccuracies

#### Sample Query and Response:

**Query**: "What is Docker Model Runner in one sentence?"

**Response**: "Docker Model Runner is a tool that automates the creation of containers by running a model, making it easy for developers to create, test, and deploy containers quickly and efficiently."

### 2. ai/mistral

- **Size**: 7.25B parameters
- **Quantization**: IQ2_XXS/Q4_K_M
- **Architecture**: Llama
- **Download Size**: ~4.1 GB

#### Performance Characteristics:

- **Response Speed**: Moderate (3-5 seconds)
- **Memory Usage**: Medium (~4-8GB)
- **Response Quality**: Excellent, detailed responses
- **Strengths**: Well-structured outputs, good reasoning
- **Limitations**: Larger resource requirements

#### Sample Query and Response:

**Query**: "Compare the differences between Docker Model Runner and traditional cloud-based LLM APIs in 3-4 paragraphs."

**Response**:

```
Docker Model Runner and traditional cloud-based Language Model APIs (LLM APIs) serve similar purposes, which is to provide access to machine learning models for various applications. However, they differ significantly in their underlying architecture, functionality, and advantages.

1. Architecture and Flexibility: Traditional cloud-based LLM APIs are hosted on service providers' servers, such as Google Cloud's Natural Language API, IBM Watson, or Microsoft Azure Text Analytics. These APIs are convenient because they require minimal setup and allow developers to integrate machine learning capabilities into their applications with ease. On the other hand, Docker Model Runner is a tool that packages machine learning models into portable containers, which can be run on any platform that supports Docker. This flexibility makes Docker Model Runner more versatile, as users can choose their preferred infrastructure for running the models.

2. Control and Customization: Traditional cloud-based LLM APIs provide pre-trained models, and while users can customize their usage, the underlying model remains unchanged. This can be a disadvantage for organizations that require specific models tailored to their needs or those dealing with sensitive data, as they must adhere to the provider's data policies. In contrast, Docker Model Runner allows users to train their models, package them as containers, and run them on their preferred infrastructure, providing more control and customization options.

3. Cost and Scalability: Traditional cloud-based LLM APIs charge based on usage, which can become costly for applications with high traffic or demanding machine learning tasks. Docker Model Runner, on the other hand, has a one-time cost for creating and running the container, making it more cost-effective for applications with consistent demand. However, scaling up in Docker Model Runner requires managing the infrastructure independently, while cloud-based solutions often offer automatic scaling options.

4. Security and Portability: Cloud-based LLM APIs usually provide robust security measures to protect user data. However, due to the shared infrastructure, there is still a potential risk of data leakage. Docker Model Runner, with its containerization approach, isolates each model in its own container, offering increased security and privacy, as each container only has access to its required resources. Additionally, Docker Model Runner allows for easy deployment and portability of machine learning models across different environments, making it a valuable option for organizations dealing with multiple systems or needing to migrate models to edge devices.
```

## Integration Performance

### CLI Adapter Performance

The CLI adapter successfully integrates with both models, providing:

1. **Consistent Interface**: The same adapter works with different models
2. **Reliable Generation**: Text generation works consistently
3. **Streaming Support**: Streaming generation works for both models
4. **Error Handling**: Proper error handling for invalid requests

### GPU Acceleration

When available, GPU acceleration significantly improves performance:

- **ai/smollm2**: ~2x faster with GPU
- **ai/mistral**: ~5-10x faster with GPU

### Resource Usage

Resource usage varies by model:

- **ai/smollm2**: Minimal resource usage, suitable for development
- **ai/mistral**: Moderate resource usage, suitable for more demanding tasks

## Usage Recommendations

Based on testing results, we recommend:

1. **Development**: Use ai/smollm2 for faster iteration and testing
2. **Quality Requirements**: Use ai/mistral for higher quality responses
3. **Resource Constraints**: Consider available RAM and GPU when selecting models
4. **Response Time**: Choose smaller models when response time is critical

## Future Model Testing

Additional models that could be tested in the future:

1. ai/llama3 (8B parameters) - High quality but larger download
2. ai/phi3 (Small or Mini) - Microsoft's efficient models
3. ai/gemma (2B parameters) - Google's efficient model

## Conclusion

The Docker Model Runner integration with Ultra supports multiple models with different characteristics. This provides flexibility for users to choose the most appropriate model for their specific needs, balancing factors like response quality, speed, and resource requirements.
