# Deploying AgentQMS Dashboard to Google Cloud Run

This guide walks you through deploying the AgentQMS Dashboard to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account** with billing enabled (free tier available)
2. **gcloud CLI** installed and configured
3. **Docker** (for local testing, optional)

## Quick Deploy (Recommended)

### Step 1: Install and Configure gcloud CLI

```bash
# Install gcloud CLI (if not already installed)
# macOS: brew install google-cloud-sdk
# Linux: Follow https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Deploy from Source (Easiest)

Cloud Run can build and deploy directly from source:

```bash
# From the project root directory
gcloud run deploy agentqms-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEMO_MODE=true \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300 \
  --port 8080
```

**Note:** If you have a Gemini API key, add it:
```bash
gcloud run deploy agentqms-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEMO_MODE=true,GEMINI_API_KEY=your_key_here \
  --memory 512Mi \
  --cpu 1
```

### Step 3: Get Your URL

After deployment completes, get your service URL:

```bash
gcloud run services describe agentqms-dashboard \
  --region us-central1 \
  --format='value(status.url)'
```

Visit the URL in your browser! 🎉

---

## Alternative: Deploy from Docker Image

If you prefer to build the Docker image first:

### Step 1: Build Docker Image

```bash
# Build the image
docker build -t gcr.io/YOUR_PROJECT_ID/agentqms-dashboard:latest .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/agentqms-dashboard:latest
```

### Step 2: Deploy to Cloud Run

```bash
gcloud run deploy agentqms-dashboard \
  --image gcr.io/YOUR_PROJECT_ID/agentqms-dashboard:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEMO_MODE=true \
  --memory 512Mi \
  --cpu 1 \
  --port 8080
```

---

## Environment Variables

### Required
- `DEMO_MODE=true` - Enables demo mode with sample artifacts

### Optional
- `GEMINI_API_KEY=xxx` - Your Gemini API key for AI features
- `PORT=8080` - Server port (Cloud Run sets this automatically)

### Set Environment Variables

```bash
# During deployment
gcloud run deploy agentqms-dashboard \
  --set-env-vars DEMO_MODE=true,GEMINI_API_KEY=your_key

# Or update existing service
gcloud run services update agentqms-dashboard \
  --region us-central1 \
  --set-env-vars DEMO_MODE=true,GEMINI_API_KEY=your_key
```

---

## Testing Locally with Docker

Before deploying, test the Docker image locally:

```bash
# Build
docker build -t agentqms-dashboard .

# Run
docker run -p 8080:8080 \
  -e DEMO_MODE=true \
  -e GEMINI_API_KEY=your_key_here \
  agentqms-dashboard

# Visit http://localhost:8080
```

---

## Automated Deployment with Cloud Build

### Option 1: Using cloudbuild.yaml

```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml

# This will:
# 1. Build Docker image
# 2. Push to Container Registry
# 3. Deploy to Cloud Run
```

### Option 2: Connect GitHub Repository

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click "Create Trigger"
3. Connect your GitHub repository
4. Set configuration file to `cloudbuild.yaml`
5. Set branch to `main` (or your default branch)
6. Save and enable

Now every push to main will automatically deploy!

---

## Updating the Deployment

### Update Environment Variables

```bash
gcloud run services update agentqms-dashboard \
  --region us-central1 \
  --update-env-vars GEMINI_API_KEY=new_key
```

### Rollback to Previous Revision

```bash
# List revisions
gcloud run revisions list --service agentqms-dashboard --region us-central1

# Rollback to specific revision
gcloud run services update-traffic agentqms-dashboard \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

---

## Monitoring and Logs

### View Logs

```bash
# Stream logs
gcloud run services logs read agentqms-dashboard \
  --region us-central1 \
  --follow

# Or in Cloud Console
# https://console.cloud.google.com/run/detail/us-central1/agentqms-dashboard/logs
```

### Check Service Status

```bash
gcloud run services describe agentqms-dashboard \
  --region us-central1
```

---

## Cost Estimation

**Free Tier (First 2 Million Requests/Month)**
- 2M requests/month free
- 360K GB-seconds/month free
- 2M CPU-seconds/month free

**After Free Tier**
- ~$0.40 per million requests
- ~$0.0000025 per GB-second
- ~$0.0000100 per CPU-second

**Estimated Monthly Cost (Light Usage)**
- 10K requests/day = 300K/month = **FREE** ✅
- 50K requests/day = 1.5M/month = **FREE** ✅
- 100K requests/day = 3M/month = ~$0.40/month 💰

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
gcloud run services logs read agentqms-dashboard --region us-central1

# Common issues:
# - Missing DEMO_MODE env var
# - Port mismatch (should be 8080)
# - Memory too low (increase to 512Mi or 1Gi)
```

### Build Fails

```bash
# Check build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log BUILD_ID
```

### CORS Issues

The backend is configured to allow all origins (`allow_origins=["*"]`). For production, you may want to restrict this:

```python
# In backend/server.py
allow_origins=["https://your-domain.com"]
```

---

## Production Considerations

### 1. Custom Domain

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service agentqms-dashboard \
  --domain your-domain.com \
  --region us-central1
```

### 2. Authentication (Optional)

```bash
# Require authentication
gcloud run services update agentqms-dashboard \
  --region us-central1 \
  --no-allow-unauthenticated
```

### 3. Increase Resources

```bash
# For higher traffic
gcloud run services update agentqms-dashboard \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2 \
  --max-instances 100
```

### 4. Set Up Monitoring

- Enable Cloud Monitoring in Cloud Console
- Set up alerts for errors and high latency
- Monitor request counts and costs

---

## Quick Reference

```bash
# Deploy
gcloud run deploy agentqms-dashboard --source . --region us-central1 --allow-unauthenticated --set-env-vars DEMO_MODE=true

# Get URL
gcloud run services describe agentqms-dashboard --region us-central1 --format='value(status.url)'

# View logs
gcloud run services logs read agentqms-dashboard --region us-central1 --follow

# Update env vars
gcloud run services update agentqms-dashboard --region us-central1 --update-env-vars KEY=value

# Delete service
gcloud run services delete agentqms-dashboard --region us-central1
```

---

## Next Steps

1. ✅ Deploy to Cloud Run
2. ✅ Test the dashboard at your Cloud Run URL
3. ✅ Set up Cloud Build triggers for CI/CD
4. ✅ Configure custom domain (optional)
5. ✅ Set up monitoring and alerts

**Need Help?** Check the [Troubleshooting Guide](docs/guides/troubleshooting.md) or open an issue.

