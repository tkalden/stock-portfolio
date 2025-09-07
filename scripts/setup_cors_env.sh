#!/bin/bash

# Setup CORS environment variables for Vercel deployment
echo "Setting up CORS environment variables..."

# Get the current project name from package.json or directory
PROJECT_NAME=$(basename $(pwd))
echo "Project name: $PROJECT_NAME"

# Construct Vercel domains
PRODUCTION_DOMAIN="https://${PROJECT_NAME}.vercel.app"
PREVIEW_PATTERN="https://*.vercel.app"

echo "Production domain: $PRODUCTION_DOMAIN"
echo "Preview pattern: $PREVIEW_PATTERN"

# Create .env.local file for Vercel
cat > .env.local << EOF
# Vercel UI URLs for CORS
VERCEL_UI_URL=$PRODUCTION_DOMAIN
VERCEL_PRODUCTION_PATTERN=$PRODUCTION_DOMAIN
VERCEL_PREVIEW_PATTERN=$PREVIEW_PATTERN

# Base allowed origins (local development)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Vercel environment
VERCEL=1
EOF

echo ""
echo "✅ Created .env.local with CORS configuration"
echo ""
echo "To deploy with these settings:"
echo "1. Add these environment variables to your Vercel project:"
echo "   - VERCEL_UI_URL: $PRODUCTION_DOMAIN"
echo "   - VERCEL_PRODUCTION_PATTERN: $PRODUCTION_DOMAIN"
echo "   - VERCEL_PREVIEW_PATTERN: $PREVIEW_PATTERN"
echo "   - ALLOWED_ORIGINS: http://localhost:3000,http://localhost:3001"
echo ""
echo "2. Or use the .env.local file:"
echo "   vercel --env-file .env.local"
