#!/bin/bash

# Get Vercel domain for the current project
echo "Getting Vercel domain..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI not found. Install it with: npm i -g vercel"
    exit 1
fi

# Get project info
PROJECT_INFO=$(vercel project ls --json 2>/dev/null | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$PROJECT_INFO" ]; then
    echo "Could not find project info. Make sure you're in the correct directory and logged in to Vercel."
    echo "Run: vercel login"
    exit 1
fi

# Construct the domain
DOMAIN="https://${PROJECT_INFO}.vercel.app"
echo "Your Vercel domain is: $DOMAIN"

# Export for use in other scripts
export VERCEL_DOMAIN="$DOMAIN"
echo "export VERCEL_DOMAIN=\"$DOMAIN\"" > .vercel_domain

echo ""
echo "To use this domain in your backend CORS:"
echo "export VERCEL_UI_URL=\"$DOMAIN\""
echo ""
echo "Or add it to your .env file:"
echo "VERCEL_UI_URL=$DOMAIN"
