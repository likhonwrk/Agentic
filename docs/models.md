---
applyTo: "backend/core/mcp_integration.py"
---

# 🤖 AI Models Guide

Agentic supports various AI models through Docker Model Runner, enabling local inference without external API dependencies.

## Recommended Models

### Production Models

| Model | Size | RAM Required | Use Case | Performance |
|-------|------|--------------|----------|-------------|
| **IBM Granite 3.1 8B Instruct** | 4.5GB | 8GB | General agents, instruction following | ⭐⭐⭐⭐⭐ |
| **Meta Llama 3.3 8B** | 5GB | 10GB | Complex reasoning, multi-step tasks | ⭐⭐⭐⭐⭐ |
| **Google Gemma 3 9B** | 5.5GB | 12GB | Tool calling, structured output | ⭐⭐⭐⭐ |
| **Microsoft Phi-4** | 2.5GB | 6GB | Fast inference, lightweight | ⭐⭐⭐⭐ |

### Development Models

| Model | Size | RAM Required | Use Case | Performance |
|-------|------|--------------|----------|-------------|
| **SmolLM2 1.7B** | 1GB | 4GB | Testing, resource-constrained | ⭐⭐⭐ |
| **TinyLlama 1.1B** | 600MB | 3GB | Rapid prototyping | ⭐⭐ |

## Model Installation

### Pull Models from Docker Hub

\`\`\`bash
# Production models
docker model pull ibm-granite/granite-3.1-8b-instruct
docker model pull meta-llama/llama-3.3-8b
docker model pull google/gemma-3-9b
docker model pull microsoft/phi-4

# Development models
docker model pull huggingface/smollm2-1.7b
docker model pull huggingface/tinyllama-1.1b
\`\`\`

### List Available Models

\`\`\`bash
# Check installed models
docker model list

# Check available models on Docker Hub
docker search ai/
\`\`\`

## Model Configuration

### Update Docker Compose

Edit `docker-compose-development.yml`:

\`\`\`yaml
services:
  llm:
    image: docker/model-runner:latest
    command: run --model ibm-granite/granite-3.1-8b-instruct --port 11434
    ports:
      - "11434:11434"
    volumes:
      - ./models:/models
    environment:
      - MODEL_CACHE_DIR=/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]  # Optional GPU acceleration
\`\`\`

### Backend Configuration

Update `backend/.env`:

\`\`\`env
LLM_ENDPOINT=http://llm:11434/v1
LLM_MODEL=ibm-granite/granite-3.1-8b-instruct
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.7
\`\`\`

## Model Comparison

### IBM Granite 3.1 8B Instruct
- **Best for**: General-purpose agents, instruction following
- **Strengths**: Excellent instruction adherence, balanced performance
- **Weaknesses**: Larger size than alternatives
- **Agent Types**: Chat, API, Data processing

\`\`\`bash
docker model pull ibm-granite/granite-3.1-8b-instruct
\`\`\`

### Meta Llama 3.3 8B
- **Best for**: Complex reasoning, multi-step planning
- **Strengths**: Superior reasoning capabilities, versatile
- **Weaknesses**: Higher memory requirements
- **Agent Types**: Browser automation, complex workflows

\`\`\`bash
docker model pull meta-llama/llama-3.3-8b
\`\`\`

### Google Gemma 3 9B
- **Best for**: Tool calling, structured output generation
- **Strengths**: Excellent tool integration, structured responses
- **Weaknesses**: Largest model size
- **Agent Types**: API integration, data extraction

\`\`\`bash
docker model pull google/gemma-3-9b
\`\`\`

### Microsoft Phi-4
- **Best for**: Fast inference, resource efficiency
- **Strengths**: Quick responses, lower resource usage
- **Weaknesses**: Less capable for complex tasks
- **Agent Types**: Simple chat, quick responses

\`\`\`bash
docker model pull microsoft/phi-4
\`\`\`

## Performance Optimization

### GPU Acceleration

Enable GPU support for faster inference:

\`\`\`yaml
# docker-compose-development.yml
services:
  llm:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
\`\`\`

### Memory Optimization

For systems with limited RAM:

\`\`\`yaml
services:
  llm:
    command: run --model microsoft/phi-4 --port 11434 --memory-limit 4g
    environment:
      - CUDA_VISIBLE_DEVICES=""  # Disable GPU if needed
\`\`\`

### Quantization

Use quantized models for better performance:

\`\`\`bash
# Pull quantized versions (when available)
docker model pull ibm-granite/granite-3.1-8b-instruct:q4_0
docker model pull meta-llama/llama-3.3-8b:q8_0
\`\`\`

## Model Switching

### Runtime Model Switching

Switch models without restarting:

\`\`\`bash
# Stop current model
docker compose stop llm

# Update docker-compose.yml with new model
# Restart with new model
docker compose up -d llm
\`\`\`

### Multiple Model Support

Run multiple models simultaneously:

\`\`\`yaml
services:
  llm-granite:
    image: docker/model-runner:latest
    command: run --model ibm-granite/granite-3.1-8b-instruct --port 11434
    ports:
      - "11434:11434"
  
  llm-phi:
    image: docker/model-runner:latest
    command: run --model microsoft/phi-4 --port 11435
    ports:
      - "11435:11435"
\`\`\`

## Custom Models

### Adding Custom Models

1. **Prepare Model**: Convert to GGUF format if needed
2. **Create Dockerfile**:

\`\`\`dockerfile
FROM docker/model-runner:latest
COPY my-custom-model.gguf /models/
CMD ["run", "--model", "/models/my-custom-model.gguf", "--port", "11434"]
\`\`\`

3. **Build and Run**:

\`\`\`bash
docker build -t my-custom-llm .
docker run -p 11434:11434 my-custom-llm
\`\`\`

## Troubleshooting

### Model Loading Issues

\`\`\`bash
# Check model status
curl http://localhost:11434/v1/models

# View model logs
docker compose logs llm

# Restart model service
docker compose restart llm
\`\`\`

### Memory Issues

\`\`\`bash
# Check system memory
free -h

# Monitor Docker memory usage
docker stats

# Reduce model size or enable swap
sudo swapon /swapfile
\`\`\`

### Performance Issues

\`\`\`bash
# Check GPU utilization (if available)
nvidia-smi

# Monitor CPU usage
htop

# Check model inference speed
curl -X POST http://localhost:11434/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "ibm-granite/granite-3.1-8b-instruct", "prompt": "Hello", "max_tokens": 10}'
\`\`\`

## Best Practices

### Model Selection
- **Development**: Use smaller models (Phi-4, SmolLM2) for faster iteration
- **Production**: Use larger models (Granite, Llama) for better quality
- **Resource-Constrained**: Use quantized models or smaller variants

### Resource Management
- **Monitor Memory**: Keep 2GB+ free RAM for system operations
- **GPU Utilization**: Enable GPU acceleration when available
- **Disk Space**: Ensure sufficient space for model storage

### Performance Tuning
- **Batch Size**: Adjust based on available memory
- **Context Length**: Use appropriate context window for your use case
- **Temperature**: Lower values (0.1-0.3) for deterministic responses

This guide helps you choose and configure the right AI model for your Agentic deployment based on your specific requirements and constraints.
