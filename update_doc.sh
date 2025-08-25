#!/bin/bash

# Documentation update script for Agentic AI Agent System
# Usage: ./update_doc.sh

set -e

echo "📚 Updating Agentic documentation..."

# Create docs directory structure
mkdir -p docs/{api,guides,examples,architecture}

# Generate API documentation
echo "🔧 Generating API documentation..."
cd backend
python -m pydoc -w main
mv *.html ../docs/api/
cd ..

# Generate frontend documentation
echo "🎨 Generating frontend documentation..."
cd frontend
npm run build:docs || echo "⚠️  Frontend docs generation skipped (not configured)"
cd ..

# Start documentation server
echo "🌐 Starting documentation server..."
if command -v docsify &> /dev/null; then
    docsify serve docs --port 3000
else
    echo "⚠️  Docsify not installed. Install with: npm i docsify-cli -g"
    echo "📖 Documentation available in ./docs directory"
fi
