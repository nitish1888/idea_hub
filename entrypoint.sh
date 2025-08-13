#!/bin/bash
# =============================================================================
# Red Hat Idea Hub - Entrypoint Script
# =============================================================================
#
# This script handles the startup of the Flask application in OpenShift
# with proper error handling and environment setup
#
# =============================================================================

set -e

# Print startup information
echo "🚀 Starting Red Hat Idea Hub..."
echo "📍 Working directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "🌐 Environment: ${FLASK_ENV:-production}"

# Check if database connection is available (optional)
if [ -n "$PG_HOST" ] && [ -n "$PG_PORT" ]; then
    echo "🔌 Testing database connection..."
    timeout 10 bash -c "echo > /dev/tcp/$PG_HOST/$PG_PORT" && echo "✅ Database connection successful" || echo "⚠️ Database connection failed (continuing anyway)"
fi

# Check if required environment variables are set
REQUIRED_VARS=("SECRET_KEY")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

# Set default values for optional variables
export FLASK_ENV=${FLASK_ENV:-production}
export DEBUG=${DEBUG:-False}
export FLASK_APP=${FLASK_APP:-app.py}

# Initialize HuggingFace cache directory
if [ ! -d "$HF_HOME" ]; then
    echo "📁 Creating HuggingFace cache directory: $HF_HOME"
    mkdir -p "$HF_HOME"
fi

# Check if mixedbread model is cached
echo "🔍 Checking for cached embedding model..."
if [ -d "$HF_HOME/models--mixedbread-ai--mxbai-embed-large-v1" ] || [ -d "$HF_HOME/hub/models--mixedbread-ai--mxbai-embed-large-v1" ]; then
    echo "✅ Mixedbread embedding model found in cache"
else
    echo "⚠️ Mixedbread model not in cache - will download on first use"
fi

# Test Flask app import
echo "🧪 Testing Flask application import..."
python -c "from app import app; print('✅ Flask app imported successfully')" || {
    echo "❌ Failed to import Flask app"
    exit 1
}

# Start the Flask application
echo "🌟 Starting Flask application..."
echo "📡 Host: ${1#--host=}"
echo "🔌 Port: ${2#--port=}"

# Execute the Flask application with passed arguments
exec python app.py "$@"
