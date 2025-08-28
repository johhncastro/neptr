#!/bin/bash

# Set the API keys
export OPENAI_API_KEY="your-openai-api-key-here"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run Neptr
echo "🤖 Starting NEPTR with enhanced TTS options..."
echo "🎤 TTS Engine: Check config.py to change voice settings"
python3 neptr.py
