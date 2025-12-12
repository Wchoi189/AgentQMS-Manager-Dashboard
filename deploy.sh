#!/bin/bash
# Quick deployment script for AgentQMS Dashboard to Google Cloud Run
# Project: vibecode-gemini3-competition

set -e

# Project configuration
PROJECT_ID="gen-lang-client-0859375571"
PROJECT_NUMBER="478428819978"
SERVICE_NAME="agentqms-dashboard"
REGION="us-central1"

echo "🚀 Deploying AgentQMS Dashboard to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "📋 Setting Google Cloud project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

# Check if user is authenticated
echo "🔐 Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "⚠️  Not authenticated. Running gcloud auth login..."
    gcloud auth login
fi

# Ask for Gemini API key (optional)
echo ""
read -p "Enter Gemini API Key (or press Enter to skip): " GEMINI_KEY

# Build environment variables
ENV_VARS="DEMO_MODE=true"
if [ ! -z "$GEMINI_KEY" ]; then
    ENV_VARS="$ENV_VARS,GEMINI_API_KEY=$GEMINI_KEY"
    echo "✅ Gemini API key will be set"
else
    echo "⚠️  No Gemini API key provided (AI features will be limited)"
fi

# Deploy to Cloud Run
echo ""
echo "🏗️  Building and deploying to Cloud Run..."
echo "This may take 5-10 minutes on first deployment..."
echo ""

gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "$ENV_VARS" \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300 \
  --port 8080

# Get the service URL
echo ""
echo "✅ Deployment complete!"
echo ""
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format='value(status.url)')

echo "🌐 Your dashboard is live at:"
echo "   $SERVICE_URL"
echo ""
echo "📊 View logs:"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION --follow"
echo ""
echo "🔧 Update environment variables:"
echo "   gcloud run services update $SERVICE_NAME --region $REGION --update-env-vars KEY=value"
echo ""
echo "🎉 Done! Open the URL above in your browser."

