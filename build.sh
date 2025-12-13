#!/bin/bash
# build.sh - Build script for Render

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p backend/data
mkdir -p chroma_data

# Initialize LLM models (this will cache them)
python -c "
from transformers import AutoTokenizer
print('Downloading embedding model...')
AutoTokenizer.from_pretrained('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
print('✅ Models downloaded successfully')
"

echo "✅ Build complete!"