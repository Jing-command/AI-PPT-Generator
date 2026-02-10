# Image Generation Setup

## Overview
This document explains how to configure separate API keys for text generation and image generation.

## Configuration Options

### Option 1: Same API Key for Both (Default)
If you use the same yunwu.ai API key for both text and image generation:

```bash
# In your .env file or environment
YUNWU_API_KEY=sk-yunwu-xxxxxxxx
```

The system will automatically use this key for both operations.

### Option 2: Separate API Keys
If you have different API keys for text and image generation:

```bash
# Main API key for text generation (OpenAI-compatible)
YUNWU_API_KEY=sk-yunwu-xxxxxxxx

# Separate API key for image generation (Gemini native API)
IMAGE_API_KEY=sk-yunwu-yyyyyyyy
```

Or use environment variables:

```bash
export YUNWU_API_KEY="sk-yunwu-xxxxxxxx"
export IMAGE_API_KEY="sk-yunwu-yyyyyyyy"
```

## API Endpoints

### Text Generation (Outline)
- **Endpoint**: `https://yunwu.ai/v1/chat/completions`
- **Model**: `gemini-3-flash-preview`
- **Format**: OpenAI-compatible

### Image Generation
- **Endpoint**: `https://yunwu.ai/v1beta/models/gemini-3-pro-image-preview:generateContent`
- **Model**: `gemini-3-pro-image-preview`
- **Format**: Gemini native API

## Testing

Run the test script to verify configuration:

```bash
# Test with separate keys
python test_image_generation.py

# Test complete data flow
python test_data_flow.py
```

## Troubleshooting

### No images generated
1. Check Celery worker logs for `[Generation]` messages
2. Verify API keys have access to the required models
3. Check yunwu.ai account balance

### "Not supported model" error
- The `gemini-3-pro-image-preview` model may not be available for your API key
- Contact yunwu.ai support or use a different provider

### Timeout errors
- Image generation can take 30-120 seconds
- Ensure Celery worker timeout is set appropriately
